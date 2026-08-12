"""
Milestone 3.10 (validation) - Full validation pass on the corrected final
modelling dataset (262 records post NDVI-fix). Checks physical plausibility
of every feature, missing values, class balance, and investigates the
composite-key duplicate question (grid_cell_id + observation_date +
presence) that was flagged but never resolved in an earlier pass.

Output: reports/milestone_3_11_validation_summary.txt
"""

import pandas as pd

DATASET_PATH = "data/processed/modelling_dataset_final.csv"
PA_POOL_PATH = "data/processed/pseudo_absence_pool.csv"
SUMMARY_PATH = "reports/milestone_3_11_validation_summary.txt"

lines = []
def log(msg=""):
    print(msg)
    lines.append(str(msg))


def main():
    df = pd.read_csv(DATASET_PATH)
    log("=== BASIC SHAPE ===")
    log(f"Records: {len(df)}, Columns: {len(df.columns)}")
    log(f"Class balance:\n{df['presence'].value_counts().to_string()}")

    log("\n=== MISSING VALUES ===")
    missing = df.isna().sum()
    log(missing[missing > 0].to_string() if missing.sum() > 0 else "None")

    log("\n=== PHYSICAL PLAUSIBILITY RANGES ===")
    checks = {
        "ndvi_nearest_composite": (-1, 1),
        "ndvi_anomaly": (-2, 2),
        "rainfall_7d": (0, None),
        "rainfall_30d": (0, None),
        "rainfall_90d": (0, None),
        "elevation_m": (0, None),
        "slope_deg": (0, 90),
        "dist_to_water_m": (0, None),
    }
    for col, (lo, hi) in checks.items():
        if col not in df.columns:
            continue
        actual_lo, actual_hi = df[col].min(), df[col].max()
        flag = ""
        if lo is not None and actual_lo < lo:
            flag += f" [BELOW MIN {lo}]"
        if hi is not None and actual_hi > hi:
            flag += f" [ABOVE MAX {hi}]"
        log(f"{col}: {actual_lo:.3f} to {actual_hi:.3f}{flag}")

    log("\n=== DUPLICATE KEY CHECK: record_key ===")
    dup_key = df["record_key"].duplicated().sum()
    log(f"Duplicate record_key values: {dup_key} (should be 0 - true unique identifier)")

    log("\n=== DUPLICATE INVESTIGATION: (grid_cell_id, observation_date, presence) ===")
    composite_dupe_mask = df.duplicated(subset=["grid_cell_id", "observation_date", "presence"], keep=False)
    composite_dupes = df[composite_dupe_mask]
    log(f"Records sharing (cell, date, presence) with >=1 other record: {len(composite_dupes)} of {len(df)}")

    if len(composite_dupes) > 0:
        by_type = composite_dupes["record_type"].value_counts()
        log(f"\nBreakdown by record_type:\n{by_type.to_string()}")

        log("\nTop grid_cell_id/date clusters (by group size):")
        grp = composite_dupes.groupby(["grid_cell_id", "observation_date", "presence"]).size().sort_values(ascending=False)
        log(grp.head(15).to_string())

        # Critical check: does any (cell, date) pair appear in BOTH presence
        # and pseudo-absence? This would mean the same space-time point was
        # labeled both 1 and 0 - a genuine contradiction, not benign.
        log("\n=== CROSS-CLASS CHECK: same (cell, date) in BOTH presence and pseudo-absence ===")
        cross = df.groupby(["grid_cell_id", "observation_date"])["presence"].nunique()
        cross_conflict = cross[cross > 1]
        log(f"(cell, date) pairs with BOTH presence AND pseudo-absence: {len(cross_conflict)}")
        if len(cross_conflict) > 0:
            log(cross_conflict.to_string())
            log("*** THIS IS A GENUINE CONTRADICTION - REQUIRES CORRECTION, NOT JUST DOCUMENTATION ***")

        # For pseudo-absence duplicates specifically: check whether the
        # underlying pool records have different scientificName values,
        # which would confirm "different species, same checklist" as the
        # legitimate explanation.
        pa_dupes = composite_dupes[composite_dupes["record_type"] == "pseudo_absence"]
        if len(pa_dupes) > 0:
            try:
                pool = pd.read_csv(PA_POOL_PATH)
                key_col = "key" if "key" in pool.columns else "record_key"
                pool_subset = pool[pool[key_col].isin(pa_dupes["record_key"])]
                if "scientificName" in pool_subset.columns:
                    log(f"\nPseudo-absence duplicate records - unique species involved: {pool_subset['scientificName'].nunique()}")
                    log(pool_subset[[key_col, "scientificName"]].drop_duplicates().to_string(index=False))
            except FileNotFoundError:
                log(f"\n(Could not cross-check species - {PA_POOL_PATH} not found)")

    log("\n=== SUMMARY ===")
    log("Validation complete. Review flags above before declaring Milestone 3 closed.")

    with open(SUMMARY_PATH, "w") as f:
        f.write("\n".join(lines))
    print(f"\nSaved to {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
