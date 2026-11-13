from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.preprocessing import StandardScaler

import cv_audit_common as cc

ORIGINAL_RESULTS_PATH = "reports/baseline_logistic_regression_cv_results.csv"
FOLDS = [0, 1, 2, 3, 4]
BASELINE_NUMERIC = [
    "rice_pct_1000m", "dist_to_nearest_rice_m", "rainfall_30d", "temp_mean_7d",
    "dewpoint_mean_7d", "wind_mean_7d", "ndvi_nearest_composite", "elevation_m",
    "slope_deg", "dist_to_water_m",
]
SEASON_CATEGORIES = ["dry_cool", "dry_hot", "long_rains", "short_rains"]
SEASON_DUMMIES = ["season_dry_hot", "season_long_rains", "season_short_rains"]
MODEL_COLUMNS = BASELINE_NUMERIC + SEASON_DUMMIES
TOLERANCES = {"n_test": 0.0, "n_presence_test": 0.0, "precision": 1e-12, "recall": 1e-12, "f1": 1e-12, "roc_auc": 1e-9}
TWO_RUN_TOLERANCE = 1e-9
REFERENCE_CM = {0: [[42, 0], [7, 1]], 1: [[2, 3], [2, 7]], 2: [[10, 10], [1, 10]], 3: [[18, 4], [6, 30]], 4: [[39, 5], [44, 25]]}
REFERENCE_AGGREGATE = {"precision": ("0.783", "0.191"), "recall": ("0.602", "0.340"), "f1": ("0.593", "0.244"), "roc_auc": ("0.854", "0.089")}
REFERENCE_CALIBRATION = {
    0: ("0.579", "0.160", "0.053", "0.020"), 1: ("0.492", "0.643", "0.750", "0.714"),
    2: ("0.519", "0.355", "0.517", "0.645"), 3: ("0.466", "0.621", "0.539", "0.586"),
    4: ("0.418", "0.611", "0.341", "0.265"),
}
REFERENCE_FOLD4 = {
    (False, "presence"): (9, 0.508, 0.459, 0.304, 0.811, 0.444),
    (False, "pseudo_absence"): (42, 0.164, 0.110, 0.003, 0.775, 0.095),
    (True, "presence"): (60, 0.431, 0.378, 0.144, 0.802, 0.350),
    (True, "pseudo_absence"): (2, 0.568, 0.568, 0.407, 0.729, 0.500),
}


def record_filter_context(run: cc.Run) -> None:
    context = {"core.autocrlf": cc.git("config", "--get", "core.autocrlf", check=False) or "unset"}
    for rel_path in cc.GATED_BLOBS:
        context[rel_path] = cc.git("check-attr", "text", "eol", "--", rel_path)
    run.parameters["filter_context"] = context


def build_season_dummies(run: cc.Run, frame: pd.DataFrame) -> pd.DataFrame:
    season = frame["season"].astype(str)
    run.check("season_values_equal_fixed_set", set(season) == set(SEASON_CATEGORIES), str(sorted(set(season))), fatal=True)
    dummies = pd.DataFrame({f"season_{c}": (season == c).astype(int) for c in SEASON_CATEGORIES[1:]})
    run.parameters["season_category_counts"] = season.value_counts().to_dict()
    run.check("season_dummy_names_and_order", list(dummies.columns) == SEASON_DUMMIES, str(list(dummies.columns)), fatal=True)
    reference_ok = bool((dummies[season == "dry_cool"].sum(axis=1) == 0).all())
    run.check("season_reference_dry_cool_all_zero", reference_ok, fatal=True)
    others_ok = all(bool((dummies.loc[season == c, f"season_{c}"] == 1).all() and (dummies[season == c].sum(axis=1) == 1).all()) for c in SEASON_CATEGORIES[1:])
    run.check("season_other_rows_exactly_own_dummy", others_ok, fatal=True)
    implicit = pd.get_dummies(frame["season"], prefix="season", drop_first=True).astype(int)
    cross_ok = list(implicit.columns) == SEASON_DUMMIES and bool((implicit.to_numpy() == dummies.to_numpy()).all())
    run.check("season_encoding_equals_get_dummies_drop_first", cross_ok, fatal=True)
    return dummies


def run_cv(frame: pd.DataFrame, dummies: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    numeric = frame[BASELINE_NUMERIC].to_numpy(float)
    season = dummies.to_numpy(float)
    target = frame["presence"].to_numpy()
    fold_ids = frame["fold"].to_numpy()
    p_hat = np.full(len(frame), np.nan)
    y_pred = np.full(len(frame), -1)
    info = []
    for fold in FOLDS:
        train, test = fold_ids != fold, fold_ids == fold
        scaler = StandardScaler()
        x_train = np.hstack([scaler.fit_transform(numeric[train]), season[train]])
        x_test = np.hstack([scaler.transform(numeric[test]), season[test]])
        model = LogisticRegression(max_iter=1000, random_state=42)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            model.fit(x_train, target[train])
        y_pred[test] = model.predict(x_test)
        p_hat[test] = model.predict_proba(x_test)[:, 1]
        info.append({
            "fold": fold, "n_train": int(train.sum()), "n_test": int(test.sum()), "params": model.get_params(),
            "n_iter": [int(v) for v in model.n_iter_], "intercept_standardised": float(model.intercept_[0]),
            "coef_standardised": dict(zip(MODEL_COLUMNS, [float(v) for v in model.coef_[0]])),
            "scaler_mean": dict(zip(BASELINE_NUMERIC, [float(v) for v in scaler.mean_])),
            "scaler_scale": dict(zip(BASELINE_NUMERIC, [float(v) for v in scaler.scale_])),
            "convergence_warnings": [str(w.message) for w in caught if issubclass(w.category, ConvergenceWarning)],
            "other_warnings": [f"{w.category.__name__}: {w.message}" for w in caught if not issubclass(w.category, ConvergenceWarning)],
        })
    predictions = frame[["record_key", "fold", "presence", "record_type", "grid_cell_id"]].copy()
    predictions["p_hat"] = p_hat
    predictions["y_pred"] = y_pred
    return predictions, info


def fold_metrics(predictions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for fold in FOLDS:
        part = predictions[predictions["fold"] == fold]
        y_true, y_hat, proba = part["presence"].to_numpy(), part["y_pred"].to_numpy(), part["p_hat"].to_numpy()
        try:
            auc = roc_auc_score(y_true, proba)
        except ValueError:
            auc = float("nan")
        tn, fp, fn, tp = confusion_matrix(y_true, y_hat, labels=[0, 1]).ravel()
        rows.append({"fold": fold, "n_test": len(part), "n_presence_test": int(y_true.sum()),
                     "precision": precision_score(y_true, y_hat, zero_division=0), "recall": recall_score(y_true, y_hat, zero_division=0),
                     "f1": f1_score(y_true, y_hat, zero_division=0), "roc_auc": auc,
                     "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)})
    return pd.DataFrame(rows)


def compare_with_original(run: cc.Run, metrics: pd.DataFrame, original: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for fold in FOLDS:
        new = metrics[metrics["fold"] == fold].iloc[0]
        old = original[original["fold"] == fold].iloc[0]
        for column, tolerance in TOLERANCES.items():
            difference = abs(float(new[column]) - float(old[column]))
            rows.append({"fold": fold, "metric": column, "original": float(old[column]), "rerun": float(new[column]),
                         "abs_difference": difference, "tolerance": tolerance, "passed": bool(difference <= tolerance)})
        tp = int(round(float(old["recall"]) * float(old["n_presence_test"])))
        fn = int(old["n_presence_test"]) - tp
        fp = int(round(tp / float(old["precision"]) - tp)) if float(old["precision"]) > 0 else -1
        tn = int(old["n_test"]) - int(old["n_presence_test"]) - fp
        printed = REFERENCE_CM[fold]
        got = [[int(new["tn"]), int(new["fp"])], [int(new["fn"]), int(new["tp"])]]
        run.check(f"confusion_matrix_fold{fold}_equals_printed_output", got == printed, f"got {got}, printed {printed}")
        run.check(f"confusion_matrix_fold{fold}_equals_counts_recomputed_from_original_csv", got == [[tn, fp], [fn, tp]], f"got {got}, recomputed {[[tn, fp], [fn, tp]]}")
    return pd.DataFrame(rows)


def check_aggregates(run: cc.Run, metrics: pd.DataFrame) -> list[str]:
    lines = []
    for column, (mean_text, sd_text) in REFERENCE_AGGREGATE.items():
        mean, sd = metrics[column].mean(), metrics[column].std(ddof=1)
        lines.append(f"  {column}: mean={mean:.3f} sd={sd:.3f} (printed {mean_text} / {sd_text})")
        run.check(f"aggregate_{column}_equals_printed_3dp", f"{mean:.3f}" == mean_text and f"{sd:.3f}" == sd_text, f"{mean:.3f}/{sd:.3f}")
    return lines


def check_diagnostics(run: cc.Run, frame: pd.DataFrame, predictions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for fold in FOLDS:
        part = predictions[predictions["fold"] == fold]
        values = (frame.loc[frame["fold"] != fold, "presence"].mean(), part["presence"].mean(), part["p_hat"].mean(), (part["p_hat"] >= 0.5).mean())
        text = tuple(f"{v:.3f}" for v in values)
        rows.append({"fold": fold, "train_presence_rate": values[0], "test_presence_rate": values[1], "mean_p_hat": values[2], "fraction_p_hat_ge_0_5": values[3]})
        run.check(f"calibration_diagnostic_fold{fold}_equals_printed_3dp", text == REFERENCE_CALIBRATION[fold], f"got {text}, printed {REFERENCE_CALIBRATION[fold]}")
    fold4 = predictions[predictions["fold"] == 4].copy()
    fold4["in_cell_0080"] = fold4["grid_cell_id"] == "cell_0080"
    fold4["positive"] = fold4["p_hat"] >= 0.5
    groups = fold4.groupby(["in_cell_0080", "record_type"]).agg(n=("p_hat", "size"), mean=("p_hat", "mean"), median=("p_hat", "median"),
                                                               min=("p_hat", "min"), max=("p_hat", "max"), fraction_ge_0_5=("positive", "mean")).reset_index()
    for row in groups.itertuples():
        expected = REFERENCE_FOLD4[(bool(row.in_cell_0080), row.record_type)]
        got = (int(row.n), round(row.mean, 3), round(row.median, 3), round(row.min, 3), round(row.max, 3), round(row.fraction_ge_0_5, 3))
        passed = got[0] == expected[0] and all(abs(a - b) < 1e-9 for a, b in zip(got[1:], expected[1:]))
        run.check(f"fold4_group_in_cell_0080={row.in_cell_0080}_{row.record_type}_equals_printed_3dp", passed, f"got {got}, printed {expected}")
    run.write_csv("m0_fold4_groups.csv", groups)
    return pd.DataFrame(rows)


def main() -> None:
    run = cc.Run("M0", ["src/cv_audit_common.py", "src/cv_audit_m0.py", "src/train_baseline_logistic_regression.py"])
    run.parameters.update({"model": "LogisticRegression(max_iter=1000, random_state=42), other parameters at installed defaults",
                           "threshold": 0.5, "tolerances": TOLERANCES, "two_run_tolerance": TWO_RUN_TOLERANCE, "model_columns": MODEL_COLUMNS})
    frame = cc.load_frame(run)
    record_filter_context(run)
    run.check("baseline_numeric_order_is_same_set_as_audit_predictors", sorted(BASELINE_NUMERIC) == sorted(cc.NUMERIC_PREDICTORS), fatal=True)
    original = pd.read_csv(cc.ROOT / ORIGINAL_RESULTS_PATH)
    run.check("original_results_has_five_folds", list(original["fold"]) == FOLDS, fatal=True)
    dummies = build_season_dummies(run, frame)

    predictions, info = run_cv(frame, dummies)
    predictions_again, _ = run_cv(frame, dummies)
    spread = float(np.max(np.abs(predictions["p_hat"].to_numpy() - predictions_again["p_hat"].to_numpy())))
    run.check("two_runs_agree_within_1e-9", spread <= TWO_RUN_TOLERANCE, f"max abs difference {spread:.3e}")
    run.check("all_probabilities_finite", bool(np.isfinite(predictions["p_hat"]).all()))
    run.check("no_p_hat_exactly_0_5", not bool((predictions["p_hat"] == 0.5).any()))
    run.check("predict_equals_p_hat_ge_0_5", bool((predictions["y_pred"].to_numpy() == (predictions["p_hat"] >= 0.5).astype(int).to_numpy()).all()))
    run.check("no_convergence_warning_in_any_fold", not any(item["convergence_warnings"] for item in info), str([i["convergence_warnings"] for i in info]))
    run.check("n_iter_below_max_iter_in_every_fold", all(max(item["n_iter"]) < 1000 for item in info), str([i["n_iter"] for i in info]))

    metrics = fold_metrics(predictions)
    comparison = compare_with_original(run, metrics, original)
    aggregate_lines = check_aggregates(run, metrics)
    calibration = check_diagnostics(run, frame, predictions)
    run.write_csv("m0_oof_predictions.csv", predictions)
    run.write_csv("m0_fold_metrics.csv", metrics)
    run.write_csv("m0_reproduction_comparison.csv", comparison)
    run.write_csv("m0_calibration_diagnostic.csv", calibration)
    run.write_json("m0_fold_models.json", info)

    failed = [a["name"] for a in run.assertions if not a["passed"]]
    worst = comparison.groupby("metric")["abs_difference"].max().to_dict()
    lines = [f"CV audit M0 run {run.dir.name}", f"HEAD {run.head}", "", "Per-fold metrics (full precision in m0_fold_metrics.csv):", metrics.round(3).to_string(index=False), "",
             "Aggregate across folds (unweighted mean, sample SD):", *aggregate_lines, "",
             "Largest absolute difference from the original results file, by metric: " + ", ".join(f"{k}={v:.3e}" for k, v in worst.items()),
             f"Two-run maximum probability difference: {spread:.3e}", "",
             "REPRODUCTION: " + ("PASSED" if not failed else "FAILED -> " + ", ".join(failed))]
    run.write_text("run_summary.txt", "\n".join(lines))
    unchanged = run.finalize()
    print("\n".join(lines))
    print(f"\nOutput directory: {run.dir}")
    if failed or not unchanged:
        run.stop("M0 reproduction criteria not met or protected files changed; see manifest.json and run_summary.txt. No code, data, fold or tolerance was changed to obtain agreement.")


if __name__ == "__main__":
    main()
