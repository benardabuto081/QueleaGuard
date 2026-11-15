from __future__ import annotations

import hashlib
import inspect
import json
import re
import warnings

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

import cv_audit_common as cc
from cv_audit_m0 import BASELINE_NUMERIC, MODEL_COLUMNS, build_season_dummies, record_filter_context
from cv_audit_r import M0_DIR, load_predictions, subset_metrics

M0_MODELS_PATH = f"{M0_DIR}/m0_fold_models.json"
M0_MODELS_BLOB = "969429e40a758b0c885d2e30bc30cb0a05afb8b3"
FOLDS = [0, 1, 2, 3, 4]
ABLATIONS = {
    "cell_0080": (4, [0, 1, 2, 3], (60, 2)), "cell_0156": (3, [0, 1, 2, 4], (27, 0)), "cell_0097": (1, [0, 2, 3, 4], (7, 0)),
    "cell_0009": (2, [0, 1, 3, 4], (5, 1)), "cell_0099": (4, [0, 1, 2, 3], (6, 2)),
}
UNIT_WEIGHT_TOLERANCE = 1e-9
STATIONARITY_TOLERANCE = 1e-3
WEIGHT_EPS = 1e-12
C_VALUE = 1.0
MAX_ITER = 1000
METRIC_KEYS = ["precision", "recall", "f1", "roc_auc"]


def digest(keys: pd.Series) -> str:
    return hashlib.sha256(",".join(str(k) for k in sorted(keys)).encode()).hexdigest()


def exact_repeat_weights(train: pd.DataFrame) -> np.ndarray:
    weights = np.empty(len(train))
    for cls in (0, 1):
        rows = (train["presence"] == cls).to_numpy()
        part = train[rows]
        group_size = part.groupby("coord_date")["record_key"].transform("size").to_numpy()
        weights[rows] = (len(part) / part["coord_date"].nunique()) / group_size
    return weights


def cell_balanced_weights(train: pd.DataFrame) -> np.ndarray:
    presence = (train["presence"] == 1).to_numpy()
    per_cell = train.loc[presence, "grid_cell_id"].value_counts()
    k = len(per_cell)
    weights = np.ones(len(train))
    weights[presence] = (presence.sum() / k) / train.loc[presence, "grid_cell_id"].map(per_cell).to_numpy()
    return weights


def kish(weights: np.ndarray) -> float:
    return float(weights.sum() ** 2 / (weights ** 2).sum()) if len(weights) else float("nan")


def record_sklearn_documentation(run: cc.Run) -> None:
    doc = LogisticRegression.__doc__
    start, end = doc.find("This class implements regularized logistic regression"), doc.find("Read more in the")
    c_block = re.search(r"\n\s+C : float.*?(?=\n\s+\w+ : )", doc, re.S)
    fit_doc = inspect.getdoc(LogisticRegression.fit)
    weight_block = re.search(r"sample_weight : .*?(?=\n\w+\n|\n\nReturns)", fit_doc, re.S)
    run.parameters["sklearn_documentation_installed_version"] = {
        "class_introduction": " ".join(doc[start:end].split()) if start >= 0 else "not found",
        "C": " ".join(c_block.group(0).split()) if c_block else "not found",
        "fit_sample_weight": " ".join(weight_block.group(0).split()) if weight_block else "not found",
        "objective_form_checked_against": "protocol 8.3: (1/2)||w||^2 + C * sum_i s_i l_i, intercept unpenalised; verified numerically per fit by the stationarity diagnostic",
    }


def fit_once(frame: pd.DataFrame, dummies: np.ndarray, train: np.ndarray, test: np.ndarray, weights: np.ndarray | None) -> dict:
    numeric = frame[BASELINE_NUMERIC].to_numpy(float)
    y = frame["presence"].to_numpy()
    scaler = StandardScaler().fit(numeric[train])
    x_train = np.hstack([scaler.transform(numeric[train]), dummies[train]])
    x_test = np.hstack([scaler.transform(numeric[test]), dummies[test]])
    w = np.ones(int(train.sum())) if weights is None else np.asarray(weights, dtype=float)
    model = LogisticRegression(max_iter=MAX_ITER, random_state=42)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        model.fit(x_train, y[train], sample_weight=w)
    beta, intercept = model.coef_[0], float(model.intercept_[0])
    p_train = np.clip(model.predict_proba(x_train)[:, 1], 1e-15, 1 - 1e-15)
    loss = -(y[train] * np.log(p_train) + (1 - y[train]) * np.log(1 - p_train))
    residual = w * (p_train - y[train])
    gradient = np.concatenate([beta + C_VALUE * (x_train.T @ residual), [C_VALUE * residual.sum()]])
    penalty = 0.5 * float(beta @ beta)
    n_numeric = len(BASELINE_NUMERIC)
    return {
        "mean": scaler.mean_, "scale": scaler.scale_, "n_seen": int(scaler.n_samples_seen_), "beta_std": beta, "intercept_std": intercept,
        "beta_orig": np.concatenate([beta[:n_numeric] / scaler.scale_, beta[n_numeric:]]),
        "intercept_orig": intercept - float((beta[:n_numeric] * scaler.mean_ / scaler.scale_).sum()),
        "n_iter": int(model.n_iter_[0]), "convergence_warnings": [str(x.message) for x in caught if issubclass(x.category, ConvergenceWarning)],
        "p_test": model.predict_proba(x_test)[:, 1], "logit_test": model.decision_function(x_test), "weights": w,
        "norm_beta_std": float(np.linalg.norm(beta)), "weighted_log_loss_sum": float((w * loss).sum()),
        "weighted_log_loss_mean": float((w * loss).sum() / w.sum()), "penalty_value": penalty,
        "objective": penalty + C_VALUE * float((w * loss).sum()), "stationarity": float(np.abs(gradient).max() / (C_VALUE * w.sum())),
        "dummies_constant": bool((dummies[train].std(axis=0) == 0).any()),
    }


def v0_reference(m0_models: list[dict], fold: int) -> dict:
    item = m0_models[fold]
    mean = np.array([item["scaler_mean"][c] for c in BASELINE_NUMERIC])
    scale = np.array([item["scaler_scale"][c] for c in BASELINE_NUMERIC])
    beta = np.array([item["coef_standardised"][c] for c in MODEL_COLUMNS])
    n_numeric = len(BASELINE_NUMERIC)
    return {"mean": mean, "scale": scale, "beta_std": beta, "intercept_std": item["intercept_standardised"],
            "beta_orig": np.concatenate([beta[:n_numeric] / scale, beta[n_numeric:]]),
            "intercept_orig": item["intercept_standardised"] - float((beta[:n_numeric] * mean / scale).sum())}


def composition_row(variant: str, cell: str, fold: int, train: pd.DataFrame, weights: np.ndarray, removed: pd.DataFrame | None) -> dict:
    changed = train[np.abs(weights - 1.0) > WEIGHT_EPS]
    row = {"variant": variant, "cell": cell, "fold": fold, "train_records": len(train), "train_presences": int((train["presence"] == 1).sum()),
           "train_background": int((train["presence"] == 0).sum()), "reweighted_records": len(changed), "reweighted_coords": int(changed["coord"].nunique()),
           "reweighted_dates": int(changed["observation_date"].nunique()), "reweighted_cells": int(changed["grid_cell_id"].nunique())}
    for cls, label in ((1, "presence"), (0, "background")):
        w = weights[(train["presence"] == cls).to_numpy()]
        row.update({f"{label}_weight_total": float(w.sum()), f"{label}_weight_min": float(w.min()) if len(w) else np.nan,
                    f"{label}_weight_median": float(np.median(w)) if len(w) else np.nan, f"{label}_weight_max": float(w.max()) if len(w) else np.nan,
                    f"{label}_kish_ess": kish(w)})
    if removed is not None:
        row.update({"removed_records": len(removed), "removed_presences": int((removed["presence"] == 1).sum()), "removed_background": int((removed["presence"] == 0).sum()),
                    "removed_coords": int(removed["coord"].nunique()), "removed_dates": int(removed["observation_date"].nunique()), "removed_cells": int(removed["grid_cell_id"].nunique())})
    return row


def record_fit(store: dict, frame: pd.DataFrame, test: np.ndarray, variant: str, cell: str, fold: int, fit: dict, ref: dict,
               v0_logit: np.ndarray, train_keys: pd.Series, v0_train_digest: str) -> None:
    scaler_equal = bool(np.array_equal(fit["mean"], ref["mean"]) and np.array_equal(fit["scale"], ref["scale"]))
    test_df = frame[test]
    p_v0, p_new = test_df["p_hat"].to_numpy(), fit["p_test"]
    key = {"variant": variant, "cell": cell, "fold": fold}
    store["fits"].append({**key, "n_train": len(train_keys), "train_digest": digest(train_keys), "train_rows_equal_v0": digest(train_keys) == v0_train_digest,
                          "scaler_equals_v0": scaler_equal, "scaler_n_samples_seen": fit["n_seen"], "n_iter": fit["n_iter"],
                          "converged": not fit["convergence_warnings"] and fit["n_iter"] < MAX_ITER, "norm_beta_std": fit["norm_beta_std"],
                          "weighted_log_loss_sum": fit["weighted_log_loss_sum"], "weighted_log_loss_mean": fit["weighted_log_loss_mean"],
                          "penalty_value": fit["penalty_value"], "objective": fit["objective"], "stationarity": fit["stationarity"],
                          "intercept_std": fit["intercept_std"], "intercept_orig": fit["intercept_orig"],
                          "any_p_exactly_0_5": bool((p_new == 0.5).any()), "any_constant_season_dummy": fit["dummies_constant"]})
    names = MODEL_COLUMNS + ["intercept"]
    std_new, std_old = list(fit["beta_std"]) + [fit["intercept_std"]], list(ref["beta_std"]) + [ref["intercept_std"]]
    orig_new, orig_old = list(fit["beta_orig"]) + [fit["intercept_orig"]], list(ref["beta_orig"]) + [ref["intercept_orig"]]
    for i, name in enumerate(names):
        store["coefs"].append({**key, "feature": name, "std_v0": std_old[i], "std_variant": std_new[i], "std_difference": std_new[i] - std_old[i],
                               "orig_v0": orig_old[i], "orig_variant": orig_new[i], "orig_difference": orig_new[i] - orig_old[i],
                               "sign_flip": bool(name != "intercept" and np.sign(std_old[i]) != np.sign(std_new[i])),
                               "std_difference_interpretable": scaler_equal})
    delta = p_new - p_v0
    store["preds"].append(pd.DataFrame({**{k: v for k, v in key.items()}, "record_key": test_df["record_key"].to_numpy(), "presence": test_df["presence"].to_numpy(),
                                        "grid_cell_id": test_df["grid_cell_id"].to_numpy(), "p_hat_v0": p_v0, "p_hat_variant": p_new, "delta": delta,
                                        "logit_v0": v0_logit, "logit_variant": fit["logit_test"]}))
    rho = spearmanr(p_v0, p_new)
    store["changes"].append({**key, "n_test": len(delta), "mean_delta": float(delta.mean()), "mean_abs_delta": float(np.abs(delta).mean()),
                             "p95_abs_delta": float(np.percentile(np.abs(delta), 95)), "max_abs_delta": float(np.abs(delta).max()),
                             "spearman_with_v0": float(getattr(rho, "statistic", rho[0])), "mean_abs_logit_delta": float(np.abs(fit["logit_test"] - v0_logit).mean())})
    m_old = subset_metrics(test_df)
    m_new = subset_metrics(test_df.assign(p_hat=p_new, y_pred=(p_new >= 0.5).astype(int)))
    row = {**key, "n_test": len(test_df), "presences": m_new["presences"], "background": m_new["background"], "flags": m_new["flags"]}
    for metric in METRIC_KEYS + ["presence_mean_p", "background_mean_p"]:
        row.update({f"{metric}_v0": m_old[metric], f"{metric}_variant": m_new[metric], f"{metric}_change": m_new[metric] - m_old[metric]})
    row.update({"mean_p_v0": float(p_v0.mean()), "mean_p_variant": float(p_new.mean()), "mean_p_change": float(p_new.mean() - p_v0.mean()),
                "predicted_positive_v0": m_old["tp"] + m_old["fp"], "predicted_positive_variant": m_new["tp"] + m_new["fp"]})
    store["metrics"].append(row)


def main() -> None:
    run = cc.Run("M1", ["src/cv_audit_common.py", "src/cv_audit_d.py", "src/cv_audit_r.py", "src/cv_audit_m0.py", "src/cv_audit_m1.py"])
    run.parameters.update({"variants": ["V1_exact_repeat", "V2_cell_balanced"] + [f"V3_ablate_{c}" for c in ABLATIONS], "ablations": {c: {"containing_fold": v[0], "folds_evaluated": v[1], "presences_background": v[2]} for c, v in ABLATIONS.items()},
                           "model": f"LogisticRegression(max_iter={MAX_ITER}, random_state=42, C={C_VALUE}); scaler fit unweighted on training rows; weights via sample_weight; test records unweighted",
                           "unit_weight_tolerance": UNIT_WEIGHT_TOLERANCE, "stationarity_tolerance": STATIONARITY_TOLERANCE,
                           "change_definitions": "delta = p_variant - p_V0 per test record; p95 and max are taken over |delta|; spearman on (p_V0, p_variant)"})
    blob = cc.blob_hash(M0_MODELS_PATH)
    run.check(f"gated_blob:{M0_MODELS_PATH}", blob == M0_MODELS_BLOB, blob, fatal=True)
    frame = load_predictions(run, cc.load_frame(run))
    record_filter_context(run)
    record_sklearn_documentation(run)
    dummies = build_season_dummies(run, frame).to_numpy(float)
    m0_models = json.loads((cc.ROOT / M0_MODELS_PATH).read_text(encoding="utf-8"))
    fold_ids = frame["fold"].to_numpy()
    store = {name: [] for name in ("fits", "coefs", "preds", "changes", "metrics", "composition")}
    refs, v0_logits, v0_digests = {}, {}, {}
    worst_p = worst_b = 0.0
    for fold in FOLDS:
        train, test = fold_ids != fold, fold_ids == fold
        refs[fold] = v0_reference(m0_models, fold)
        fit = fit_once(frame, dummies, train, test, None)
        v0_logits[fold], v0_digests[fold] = fit["logit_test"], digest(frame.loc[train, "record_key"])
        worst_p = max(worst_p, float(np.abs(fit["p_test"] - frame.loc[test, "p_hat"].to_numpy()).max()))
        worst_b = max(worst_b, float(np.abs(fit["beta_std"] - refs[fold]["beta_std"]).max()))
        run.check(f"v0_scaler_refit_equals_m0_fold{fold}", bool(np.array_equal(fit["mean"], refs[fold]["mean"]) and np.array_equal(fit["scale"], refs[fold]["scale"])), fatal=True)
    run.check("unit_weight_refit_reproduces_m0_probabilities", worst_p <= UNIT_WEIGHT_TOLERANCE, f"max abs difference {worst_p:.3e}", fatal=True)
    run.check("unit_weight_refit_reproduces_m0_standardised_coefficients", worst_b <= UNIT_WEIGHT_TOLERANCE, f"max abs difference {worst_b:.3e}", fatal=True)

    for variant, builder in (("V1_exact_repeat", exact_repeat_weights), ("V2_cell_balanced", cell_balanced_weights)):
        for fold in FOLDS:
            train, test = fold_ids != fold, fold_ids == fold
            train_df = frame[train]
            weights = builder(train_df)
            presence = (train_df["presence"] == 1).to_numpy()
            totals_ok = bool(np.isclose(weights[presence].sum(), presence.sum()) and np.isclose(weights[~presence].sum(), (~presence).sum()) and np.isclose(weights.sum(), len(weights)))
            run.check(f"{variant}_fold{fold}_class_and_overall_weight_totals_preserved", totals_ok, f"{weights[presence].sum():.6f}/{presence.sum()} and {weights[~presence].sum():.6f}/{(~presence).sum()}")
            run.check(f"{variant}_fold{fold}_weights_finite_and_positive", bool(np.isfinite(weights).all() and (weights > 0).all()))
            fit = fit_once(frame, dummies, train, test, weights)
            record_fit(store, frame, test, variant, "", fold, fit, refs[fold], v0_logits[fold], train_df["record_key"], v0_digests[fold])
            store["composition"].append(composition_row(variant, "", fold, train_df, weights, None))

    for cell, (containing, evaluated, counts) in ABLATIONS.items():
        in_cell = (frame["grid_cell_id"] == cell).to_numpy()
        cell_df = frame[in_cell]
        got = (int((cell_df["presence"] == 1).sum()), int((cell_df["presence"] == 0).sum()))
        run.check(f"{cell}_counts_equal_protocol_and_all_records_in_containing_fold", got == counts and set(cell_df["fold"]) == {containing}, f"{got}, folds {sorted(set(cell_df['fold']))}")
        run.check(f"{cell}_evaluated_folds_are_all_folds_not_containing_it", evaluated == [f for f in FOLDS if f != containing], str(evaluated))
        base = fold_ids != containing
        run.check(f"{cell}_containing_fold_training_digest_equals_V0_so_no_ablated_fit_is_evaluated",
                  digest(frame.loc[base, "record_key"]) == digest(frame.loc[base & ~in_cell, "record_key"]) == v0_digests[containing])
        for fold in evaluated:
            train, test = (fold_ids != fold) & ~in_cell, fold_ids == fold
            run.check(f"{cell}_fold{fold}_test_fold_has_no_cell_records", not bool((test & in_cell).any()))
            fit = fit_once(frame, dummies, train, test, None)
            train_df = frame[train]
            record_fit(store, frame, test, f"V3_ablate_{cell}", cell, fold, fit, refs[fold], v0_logits[fold], train_df["record_key"], v0_digests[fold])
            store["composition"].append(composition_row(f"V3_ablate_{cell}", cell, fold, train_df, fit["weights"], frame[(fold_ids != fold) & in_cell]))

    fits = pd.DataFrame(store["fits"])
    shared = fits[fits["variant"].isin(["V1_exact_repeat", "V2_cell_balanced"])]
    run.check("V1_V2_training_rows_and_scaler_equal_V0_in_every_fold", bool(shared["train_rows_equal_v0"].all() and shared["scaler_equals_v0"].all()))
    run.check("all_fits_converged_below_max_iter", bool(fits["converged"].all()), ", ".join(f"{r.variant}/{r.cell}/{r.fold}" for r in fits[~fits["converged"]].itertuples()))
    run.check("no_fit_has_p_hat_exactly_0_5", not bool(fits["any_p_exactly_0_5"].any()))
    run.check("no_constant_season_dummy_in_any_training_set", not bool(fits["any_constant_season_dummy"].any()))
    run.check("weighted_fits_are_stationary_for_the_documented_objective", bool((fits["stationarity"] <= STATIONARITY_TOLERANCE).all()), f"largest {fits['stationarity'].max():.3e}")
    run.write_csv("m1_fits.csv", fits)
    run.write_csv("m1_coefficients.csv", pd.DataFrame(store["coefs"]))
    run.write_csv("m1_predictions.csv", pd.concat(store["preds"]))
    changes, metrics = pd.DataFrame(store["changes"]), pd.DataFrame(store["metrics"])
    run.write_csv("m1_prediction_change_summary.csv", changes)
    run.write_csv("m1_metrics_comparison.csv", metrics)
    run.write_csv("m1_composition.csv", pd.DataFrame(store["composition"]))

    failed = [a["name"] for a in run.assertions if not a["passed"]]
    lines = [f"CV audit M1 run {run.dir.name}", f"HEAD {run.head}", "", f"Unit-weight refit reproduces M0: max probability difference {worst_p:.3e}, max coefficient difference {worst_b:.3e}", "",
             "Paired change in p_hat versus V0, by variant, ablated cell and evaluated fold:",
             changes[["variant", "cell", "fold", "n_test", "mean_delta", "mean_abs_delta", "p95_abs_delta", "max_abs_delta", "spearman_with_v0"]].round(3).to_string(index=False), "",
             "Metrics, V0 -> variant (none designated headline):",
             metrics[["variant", "cell", "fold", "precision_v0", "precision_variant", "recall_v0", "recall_variant", "f1_v0", "f1_variant", "roc_auc_v0", "roc_auc_variant", "mean_p_v0", "mean_p_variant"]].round(3).to_string(index=False), "",
             "Fit diagnostics:", fits[["variant", "cell", "fold", "n_train", "n_iter", "converged", "norm_beta_std", "weighted_log_loss_mean", "stationarity"]].round(4).to_string(index=False), "",
             "Failed non-fatal checks: " + (", ".join(failed) if failed else "none")]
    run.write_text("run_summary.txt", "\n".join(lines))
    unchanged = run.finalize()
    print("\n".join(lines))
    print(f"\nOutput directory: {run.dir}")
    if not unchanged:
        raise SystemExit("STOPPED: protected inputs or existing audit files changed during the run")


if __name__ == "__main__":
    main()
