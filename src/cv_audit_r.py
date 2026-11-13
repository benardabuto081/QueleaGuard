from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

import cv_audit_common as cc
from cv_audit_d import banded_morans_i

M0_DIR = "reports/cv_audit/M0_20261113T063421Z_fcb5193"
OOF_PATH = f"{M0_DIR}/m0_oof_predictions.csv"
M0_METRICS_PATH = f"{M0_DIR}/m0_fold_metrics.csv"
M0_BLOBS = {OOF_PATH: "6d528a24c26db3c63747f92392d2316360046f6c", M0_METRICS_PATH: "045fa666c660e3e669001ce6c18fe2e1c66f2ddb"}
FOLDS = [0, 1, 2, 3, 4]
FOCAL = {4: "cell_0080", 3: "cell_0156"}
MIN_PER_CLASS = 3
PROTOCOL_COUNTS = {
    4: {"All": (113, 69, 44), "Focal": (62, 60, 2), "Rest": (51, 9, 42)},
    3: {"All": (58, 36, 22), "Focal": (27, 27, 0), "Rest": (31, 9, 22)},
}
PROTOCOL_REST_PRESENCE = {4: (2, 5), 3: (5, 5)}
PROTOCOL_CELL_TOTAL = {4: 23.0, 3: 6.0}
METRIC_COLUMNS = ["recall", "precision", "f1", "roc_auc"]


def load_predictions(run: cc.Run, frame: pd.DataFrame) -> pd.DataFrame:
    for rel_path, expected in M0_BLOBS.items():
        actual = cc.blob_hash(rel_path)
        run.check(f"gated_blob:{rel_path}", actual == expected, actual, fatal=True)
    pred = pd.read_csv(cc.ROOT / OOF_PATH)
    run.check("m0_predictions_266_unique_keys", len(pred) == 266 and pred["record_key"].is_unique and set(pred["record_key"]) == set(frame["record_key"]), fatal=True)
    merged = frame.merge(pred, on="record_key", how="left", suffixes=("", "_m0"), validate="one_to_one")
    same = all(bool((merged[c] == merged[f"{c}_m0"]).all()) for c in ("fold", "presence", "grid_cell_id", "record_type"))
    run.check("m0_predictions_agree_with_dataset_on_fold_class_cell_type", same, fatal=True)
    run.check("m0_p_hat_finite_and_inside_unit_interval", bool(np.isfinite(merged["p_hat"]).all() and merged["p_hat"].between(0, 1).all()), fatal=True)
    run.check("m0_y_pred_equals_p_hat_ge_0_5", bool((merged["y_pred"] == (merged["p_hat"] >= 0.5).astype(int)).all()), fatal=True)
    return merged.drop(columns=[c for c in merged.columns if c.endswith("_m0")])


def subset_metrics(part: pd.DataFrame, weights: np.ndarray | None = None) -> dict:
    y, p, pred = part["presence"].to_numpy(), part["p_hat"].to_numpy(), part["y_pred"].to_numpy()
    w = np.ones(len(part)) if weights is None else np.asarray(weights, dtype=float)
    tp, fn = float(w[(y == 1) & (pred == 1)].sum()), float(w[(y == 1) & (pred == 0)].sum())
    fp, tn = float(w[(y == 0) & (pred == 1)].sum()), float(w[(y == 0) & (pred == 0)].sum())
    n_pos, n_neg = int((y == 1).sum()), int((y == 0).sum())
    limited = n_pos < MIN_PER_CLASS or n_neg < MIN_PER_CLASS
    presences = part[part["presence"] == 1]
    out = {"records": len(part), "presences": n_pos, "background": n_neg, "presence_cells": int(presences["grid_cell_id"].nunique()),
           "presence_coords": int(presences["coord"].nunique()), "presence_dates": int(presences["observation_date"].nunique()),
           "all_distinct_coords": int(part["coord"].nunique()), "tn": tn, "fp": fp, "fn": fn, "tp": tp,
           "recall": tp / (tp + fn) if tp + fn > 0 else float("nan"), "precision": float("nan"), "f1": float("nan"), "roc_auc": float("nan")}
    out["recall_status"] = "reported" if tp + fn > 0 else "undefined (TP+FN=0)"
    out["precision_status"] = out["f1_status"] = out["auc_status"] = "not reported: fewer than 3 records in a class"
    if not limited:
        out["precision_status"] = "reported" if tp + fp > 0 else "undefined (TP+FP=0)"
        out["f1_status"] = "reported" if 2 * tp + fp + fn > 0 else "undefined (denominator 0)"
        if tp + fp > 0:
            out["precision"] = tp / (tp + fp)
        if 2 * tp + fp + fn > 0:
            out["f1"] = 2 * tp / (2 * tp + fp + fn)
        out["roc_auc"] = float(roc_auc_score(y, p, sample_weight=w))
        out["auc_status"] = "reported"
    for label, cls in (("presence", 1), ("background", 0)):
        values = p[y == cls]
        out[f"{label}_mean_p"] = float(values.mean()) if values.size else float("nan")
        out[f"{label}_median_p"] = float(np.median(values)) if values.size else float("nan")
        out[f"{label}_min_p"] = float(values.min()) if values.size else float("nan")
        out[f"{label}_max_p"] = float(values.max()) if values.size else float("nan")
        out[f"{label}_fraction_ge_0_5"] = float((values >= 0.5).mean()) if values.size else float("nan")
    out["flags"] = "; ".join(flag for flag, hit in (("<3 presence cells", out["presence_cells"] < 3),
                                                  ("limited: fewer than 3 records in a class", limited)) if hit)
    return out


def r1_site_table(run: cc.Run, frame: pd.DataFrame) -> list[str]:
    cells = sorted(frame.loc[frame["presence"] == 1, "grid_cell_id"].unique())
    rows = []
    for (fold, cell), group in frame[frame["grid_cell_id"].isin(cells)].groupby(["fold", "grid_cell_id"]):
        pres, back = group[group["presence"] == 1], group[group["presence"] == 0]
        row = {"fold": fold, "grid_cell_id": cell, "records": len(group), "presences": len(pres), "background": len(back),
               "presence_coords": pres["coord"].nunique(), "presence_dates": pres["observation_date"].nunique()}
        for label, part in (("presence", pres), ("background", back)):
            has = len(part) > 0
            row[f"{label}_p_min"] = part["p_hat"].min() if has else np.nan
            row[f"{label}_p_median"] = part["p_hat"].median() if has else np.nan
            row[f"{label}_p_max"] = part["p_hat"].max() if has else np.nan
            row[f"{label}_fraction_ge_0_5"] = float((part["p_hat"] >= 0.5).mean()) if has else np.nan
        rows.append(row)
    site = pd.DataFrame(rows)
    run.write_csv("r1_presence_cell_table.csv", site)
    background = []
    for fold in FOLDS:
        values = frame[(frame["fold"] == fold) & (frame["presence"] == 0)]["p_hat"]
        background.append({"fold": fold, **cc.summarise(values), "fraction_ge_0_5": float((values >= 0.5).mean())})
    run.write_csv("r1_background_p_hat_by_fold.csv", pd.DataFrame(background))
    return [f"R1: {len(site)} fold-cell rows for {len(cells)} presence-bearing cells; background p_hat fraction >= 0.5 by fold: "
            + ", ".join(f"fold {r['fold']}={r['fraction_ge_0_5']:.3f}" for r in background) + "."]


def decomposition(run: cc.Run, frame: pd.DataFrame, fold: int, cell: str) -> list[dict]:
    test = frame[frame["fold"] == fold]
    inside = test["grid_cell_id"] == cell
    subsets = {"All": test, "Focal": test[inside], "Rest": test[~inside]}
    rows = [{"fold": fold, "focal_cell": cell, "subset": name, **subset_metrics(part)} for name, part in subsets.items()]
    for name, expected in PROTOCOL_COUNTS[fold].items():
        got = rows[list(subsets).index(name)]
        run.check(f"R_fold{fold}_{name}_counts_equal_protocol", (got["records"], got["presences"], got["background"]) == expected, str((got["records"], got["presences"], got["background"])))
    rest = rows[2]
    run.check(f"R_fold{fold}_Rest_presence_cells_and_coordinates", (rest["presence_cells"], rest["presence_coords"]) == PROTOCOL_REST_PRESENCE[fold], str((rest["presence_cells"], rest["presence_coords"])))
    presence = test["presence"] == 1
    per_cell = test.loc[presence, "grid_cell_id"].value_counts()
    k = len(per_cell)
    weights = np.where(presence, (presence.sum() / k) / test["grid_cell_id"].map(per_cell).fillna(1).to_numpy(), 1.0)
    totals = pd.Series(weights[presence.to_numpy()]).groupby(test.loc[presence, "grid_cell_id"].to_numpy()).sum()
    run.check(f"R_fold{fold}_cell_weighted_each_presence_cell_totals_{PROTOCOL_CELL_TOTAL[fold]:g}", bool(np.allclose(totals, PROTOCOL_CELL_TOTAL[fold])), f"K={k}, totals {totals.round(6).tolist()}")
    rows.append({"fold": fold, "focal_cell": cell, "subset": "Cell-weighted", **subset_metrics(test, weights)})
    return rows


def r4_leave_one_cell_out(run: cc.Run, frame: pd.DataFrame, full: pd.DataFrame, rests: dict[int, dict]) -> list[str]:
    rows = []
    for fold in FOLDS:
        test = frame[frame["fold"] == fold]
        for cell in sorted(test.loc[test["presence"] == 1, "grid_cell_id"].unique()):
            in_cell = test["grid_cell_id"] == cell
            has_background = bool((in_cell & (test["presence"] == 0)).any())
            variants = {"primary_cell_removed": test[~in_cell]}
            if has_background:
                variants["alt_presences_removed_background_kept"] = test[~(in_cell & (test["presence"] == 1))]
            for variant, part in variants.items():
                metrics = subset_metrics(part)
                notes = []
                if metrics["presence_cells"] == 1:
                    notes.append("single presence cell remaining")
                if variant == "primary_cell_removed" and not has_background:
                    notes.append("coincides with the alt variant (cell has no background in this fold); reported once")
                if variant == "primary_cell_removed" and FOCAL.get(fold) == cell:
                    notes.append("also the R2 Rest" if fold == 4 else "also the R3 Rest")
                    for column in METRIC_COLUMNS + ["tn", "fp", "fn", "tp"]:
                        same = np.isclose(metrics[column], rests[fold][column], rtol=0, atol=1e-12, equal_nan=True)
                        run.check(f"R4_primary_equals_Rest_fold{fold}_{column}", bool(same), f"{metrics[column]} vs {rests[fold][column]}")
                rows.append({"fold": fold, "removed_cell": cell, "variant": variant, "cell_presences": int((in_cell & (test["presence"] == 1)).sum()),
                             "cell_background": int((in_cell & (test["presence"] == 0)).sum()), **metrics, "notes": "; ".join(notes)})
    table = pd.DataFrame(rows)
    run.write_csv("r4_leave_one_presence_cell_out.csv", table)
    summary = []
    for (fold, variant), group in table.groupby(["fold", "variant"]):
        for metric in METRIC_COLUMNS:
            values = group[metric].dropna()
            summary.append({"fold": fold, "variant": variant, "metric": metric, "full_fold_value": float(full.loc[full["fold"] == fold, metric].iloc[0]),
                            "min_over_removed_cells": float(values.min()) if len(values) else np.nan, "max_over_removed_cells": float(values.max()) if len(values) else np.nan,
                            "cells_with_value": len(values), "cells_removed": len(group)})
    summary = pd.DataFrame(summary)
    run.write_csv("r4_min_max_summary.csv", summary)
    primary = summary[summary["variant"] == "primary_cell_removed"]
    lines = ["R4 primary (cell removed), min-max over removed cells beside the full-fold value (a range, not an interval):"]
    for row in primary.itertuples():
        lines.append(f"  fold {row.fold} {row.metric}: full={row.full_fold_value:.3f} range=[{row.min_over_removed_cells:.3f}, {row.max_over_removed_cells:.3f}] defined for {row.cells_with_value} of {row.cells_removed} cells")
    return lines


def band_counts(distance: np.ndarray, allowed: np.ndarray) -> list[dict]:
    rows = []
    for lower, upper in cc.BANDS_KM:
        mask = (distance >= lower) & (distance < upper) & allowed
        np.fill_diagonal(mask, False)
        degree = mask.sum(axis=1)
        pairs = int(degree.sum() // 2)
        rows.append({"band_lo_km": lower, "band_hi_km": upper, "pairs": pairs, "participating_points": int((degree > 0).sum()),
                     "max_point_pair_share": float(degree.max() / pairs) if pairs else float("nan"),
                     "meets_30_pair_minimum": pairs >= cc.MIN_PAIRS_PER_BAND})
    return rows


def r5_residual_autocorrelation(run: cc.Run, frame: pd.DataFrame) -> list[str]:
    frame = frame.assign(residual=frame["presence"] - frame["p_hat"])
    prepared, unit_tables, count_rows = [], [], []
    for cls, label in ((1, "presence"), (0, "background")):
        part = frame[frame["presence"] == cls]
        units = part.groupby("coord").agg(latitude=("latitude", "first"), longitude=("longitude", "first"), fold=("fold", "first"), fold_n=("fold", "nunique"),
                                          grid_cell_id=("grid_cell_id", "first"), records=("record_key", "size"), mean_residual=("residual", "mean")).reset_index()
        run.check(f"R5_{label}_each_coordinate_in_one_fold", bool((units["fold_n"] == 1).all()))
        distance = cc.distance_matrix(units["latitude"], units["longitude"])
        nearest = (distance + np.diag(np.full(len(units), np.inf))).min()
        run.check(f"R5_{label}_no_zero_distance_pairs", bool(nearest > 0), f"smallest distance {nearest:.6f} km")
        folds, cells = units["fold"].to_numpy(), units["grid_cell_id"].to_numpy()
        same_fold, same_cell = folds[:, None] == folds[None, :], cells[:, None] == cells[None, :]
        strata = (("within_fold", same_fold), ("cross_fold", ~same_fold))
        for stratum, allowed in strata:
            count_rows += [{"class": label, "stratum": stratum, "n_units": len(units), **row} for row in band_counts(distance, allowed)]
        unit_tables.append(units.drop(columns=["fold_n"]).assign(**{"class": label}))
        prepared.append((label, units, distance, same_cell, strata))
    counts = pd.DataFrame(count_rows)
    run.write_csv("r5_feasibility_counts_before_statistics.csv", counts)
    presence_pairs = counts[counts["class"] == "presence"].groupby("stratum")["pairs"].sum().to_dict()
    run.check("R5_presence_pairs_83_within_323_cross", presence_pairs == {"within_fold": 83, "cross_fold": 323}, str(presence_pairs))
    run.write_csv("r5_residual_units.csv", pd.concat(unit_tables)[["class", "coord", "latitude", "longitude", "fold", "grid_cell_id", "records", "mean_residual"]])
    stats = []
    for label, units, distance, same_cell, strata in prepared:
        values = units["mean_residual"].to_numpy(float)
        for stratum, allowed in strata:
            stats += [{"class": label, "stratum": stratum, "unit": "distinct coordinate, mean residual", **row} for row in banded_morans_i(values, distance, allowed, same_cell)]
    table = pd.DataFrame(stats)
    run.write_csv("r5_residual_morans_i.csv", table)
    lines = ["R5 bands meeting the predeclared 30-pair minimum, by class and stratum (counts-only pre-check):"]
    for (label, stratum), group in counts.groupby(["class", "stratum"]):
        passing = int(group["meets_30_pair_minimum"].sum())
        verdict = "" if passing else " -> not estimable under this design"
        lines.append(f"  {label} {stratum}: units={group['n_units'].iloc[0]}, pairs per band={group['pairs'].tolist()}, bands meeting minimum={passing}{verdict}")
    return lines


def main() -> None:
    run = cc.Run("R", ["src/cv_audit_common.py", "src/cv_audit_d.py", "src/cv_audit_r.py"])
    run.parameters.update({"m0_inputs": M0_BLOBS, "focal_cells": FOCAL, "min_records_per_class": MIN_PER_CLASS, "bands_km": cc.BANDS_KM,
                           "min_pairs_per_band": cc.MIN_PAIRS_PER_BAND, "r5_residual": "y - p_hat (raw), mean per distinct coordinate within class",
                           "r5_moran_units": "n and the mean residual cover all distinct coordinates of the class; the stratum restricts only the pair weights"})
    frame = load_predictions(run, cc.load_frame(run))
    full = pd.DataFrame([{"fold": f, **subset_metrics(frame[frame["fold"] == f])} for f in FOLDS])
    run.write_csv("r_full_fold_metrics_from_m0_predictions.csv", full)
    m0 = pd.read_csv(cc.ROOT / M0_METRICS_PATH)
    for column in ("tn", "fp", "fn", "tp"):
        run.check(f"R_full_fold_{column}_equals_m0_metrics", bool((full[column].to_numpy() == m0[column].to_numpy()).all()))
    for column in METRIC_COLUMNS:
        run.check(f"R_full_fold_{column}_equals_m0_metrics_within_1e-12", bool(np.allclose(full[column], m0[column], rtol=0, atol=1e-12)))
    lines = r1_site_table(run, frame)
    decomposed = [row for fold in (4, 3) for row in decomposition(run, frame, fold, FOCAL[fold])]
    table = pd.DataFrame(decomposed)
    table.insert(0, "analysis", np.where(table["fold"] == 4, "R2", "R3"))
    run.write_csv("r2_r3_decomposition.csv", table)
    rests = {int(r["fold"]): r for r in decomposed if r["subset"] == "Rest"}
    columns = ["analysis", "subset", "records", "presences", "background", "tn", "fp", "fn", "tp", "recall", "precision", "f1", "roc_auc", "flags"]
    lines += ["", "R2 (Fold 4, focal cell_0080) and R3 (Fold 3, focal cell_0156); Cell-weighted confusion cells are weighted counts:", table[columns].round(3).to_string(index=False), ""]
    lines += r4_leave_one_cell_out(run, frame, full, rests) + [""] + r5_residual_autocorrelation(run, frame) + [""]
    failed = [a["name"] for a in run.assertions if not a["passed"]]
    lines.append("Failed non-fatal checks: " + (", ".join(failed) if failed else "none"))
    run.write_text("run_summary.txt", f"CV audit R run {run.dir.name}\nHEAD {run.head}\n\n" + "\n".join(lines))
    unchanged = run.finalize()
    print("\n".join(lines))
    print(f"\nOutput directory: {run.dir}")
    if not unchanged:
        raise SystemExit("STOPPED: protected inputs or existing audit files changed during the run")


if __name__ == "__main__":
    main()
