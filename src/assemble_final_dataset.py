"""
Milestone 3.10 (final, corrected) - Assemble the complete modelling dataset,
now with the NDVI quality-filter fix (Task 190) applied, and a post-merge
completeness filter that drops any record missing NDVI - not just presence
records pre-dating year 2000, but any record (presence or pseudo-absence)
that predates MODIS's first valid composite (2000-02-18). This generalizes
the exclusion rule from Log Entry 006 rather than relying on the approximate
year>=2000 proxy alone.

Output: data/processed/modelling_dataset_final.csv
        reports/milestone_3_10_final_assembly_summary.txt
"""

import pandas as pd

OCCURRENCES_PATH = "data/processed/occurrences_with_grid_cell.csv"
PSEUDO_ABSENCES_PATH = "data/processed/pseudo_absences_final.csv"
RAINFALL_PRESENCE = "data/processed/rainfall_features.csv"
RAINFALL_PA = "data/processed/rainfall_features_pseudo_absence.csv"
MET_PRESENCE = "data/processed/meteorology_features.csv"
MET_PA = "data/processed/meteorology_features_pseudo_absence.csv"
NDVI_PRESENCE = "data/processed/ndvi_features.csv"
NDVI_PA = "data/processed/ndvi_features_pseudo_absence.csv"
TERRAIN_PATH = "data/processed/terrain_features.csv"
HYDROLOGY_PATH = "data/processed/hydrology_features.csv"
OUTPUT_PATH = "data/processed/modelling_dataset_final.csv"
SUMMARY_PATH = "reports/milestone_3_10_final_assembly_summary.txt"


def main():
    # --- Presence records ---
    occ = pd.read_csv(OCCURRENCES_PATH)
    occ["year"] = pd.to_numeric(occ["year"], errors="coerce")
    presences = occ[(occ["year"] >= 2000) & (occ["grid_cell_id"].notna())].copy()
    presences = presences.rename(columns={"key": "record_key"})
    presences["presence"] = 1
    presences["record_type"] = "presence"
    presences["observation_date"] = presences["eventDate"].str[:10]
    presences = presences[["record_key", "grid_cell_id", "observation_date", "presence", "record_type", "within_scheme_boundary"]]

    # --- Pseudo-absence records ---
    pa = pd.read_csv(PSEUDO_ABSENCES_PATH)
    pa = pa.rename(columns={"key": "record_key", "eventDate": "observation_date"})
    pa["observation_date"] = pa["observation_date"].astype(str).str[:10]
    pa = pa[["record_key", "grid_cell_id", "observation_date", "presence", "within_scheme_boundary"]]
    pa["record_type"] = "pseudo_absence"

    combined = pd.concat([presences, pa], ignore_index=True)
    print(f"Combined base records: {len(combined)} ({(combined['presence']==1).sum()} presence, {(combined['presence']==0).sum()} pseudo-absence)")

    # --- Rainfall ---
    rainfall = pd.concat([
        pd.read_csv(RAINFALL_PRESENCE)[["record_key", "rainfall_7d", "rainfall_30d", "rainfall_90d"]],
        pd.read_csv(RAINFALL_PA)[["record_key", "rainfall_7d", "rainfall_30d", "rainfall_90d"]],
    ], ignore_index=True)
    combined = combined.merge(rainfall, on="record_key", how="left")

    # --- Meteorology ---
    met_cols = ["record_key", "temp_mean_7d", "dewpoint_mean_7d", "wind_mean_7d",
                "temp_same_day", "dewpoint_same_day", "wind_same_day"]
    met = pd.concat([
        pd.read_csv(MET_PRESENCE)[met_cols],
        pd.read_csv(MET_PA)[met_cols],
    ], ignore_index=True)
    combined = combined.merge(met, on="record_key", how="left")

    # --- NDVI (corrected via Task 190 quality-filter fix) ---
    ndvi_cols = ["record_key", "ndvi_nearest_composite", "ndvi_anomaly"]
    ndvi = pd.concat([
        pd.read_csv(NDVI_PRESENCE)[ndvi_cols],
        pd.read_csv(NDVI_PA)[ndvi_cols],
    ], ignore_index=True)
    combined = combined.merge(ndvi, on="record_key", how="left")

    # --- Terrain (static, per grid cell) ---
    terrain = pd.read_csv(TERRAIN_PATH)
    combined = combined.merge(terrain, on="grid_cell_id", how="left")

    # --- Hydrology (static, per grid cell) ---
    hydrology = pd.read_csv(HYDROLOGY_PATH)
    combined = combined.merge(hydrology, on="grid_cell_id", how="left")

    # --- Post-merge completeness filter (generalizes Log Entry 006) ---
    # NDVI is a required, non-optional core feature. Any record - presence
    # or pseudo-absence - that predates MODIS's first valid good-quality
    # composite (2000-02-18) will have no NDVI value after the Task 190 fix.
    # This is a genuine data availability constraint, not a quality
    # judgement, and is handled identically to the original 8 pre-2000
    # presence exclusions in Log Entry 006: excluded, not backfilled.
    pre_filter_count = len(combined)
    dropped = combined[combined["ndvi_nearest_composite"].isna()]
    if len(dropped) > 0:
        print(f"\nDropping {len(dropped)} record(s) with no valid NDVI composite (MODIS temporal boundary):")
        print(dropped[["record_key", "grid_cell_id", "observation_date", "record_type"]].to_string(index=False))
    combined = combined[combined["ndvi_nearest_composite"].notna()].copy()

    combined.to_csv(OUTPUT_PATH, index=False)
    print(f"\nFinal modelling dataset: {len(combined)} records, {len(combined.columns)} columns")
    print(f"({pre_filter_count} pre-filter -> {len(combined)} post-filter)")
    print(f"Saved to {OUTPUT_PATH}")

    print("\nMissing value summary (all columns):")
    missing = combined.isna().sum()
    print(missing[missing > 0] if missing.sum() > 0 else "No missing values.")

    print("\nClass balance:")
    print(combined["presence"].value_counts())

    summary = f"""Milestone 3.10 - Final Modelling Dataset Assembly Summary (corrected)
==============================================================

Total records: {len(combined)}
Presence: {(combined['presence']==1).sum()}
Pseudo-absence: {(combined['presence']==0).sum()}
Columns: {len(combined.columns)}

Corrections applied in this assembly:
- Task 190: NDVI extraction now filters to good-quality composites before
  nearest-composite selection, eliminating 8 records that previously held
  the MODIS fill value (-3000) as if it were valid NDVI.
- Post-fix, 4 pseudo-absence records (cell_0283 x2, cell_0146 x2, all
  dated Jan 2000) were found to predate MODIS's first good-quality
  composite (2000-02-18) and have no valid NDVI value. Excluded, not
  backfilled, per the same precedent established in Log Entry 006 for
  the 8 pre-2000 presence records. Final class balance is
  {(combined['presence']==1).sum()} presence : {(combined['presence']==0).sum()} pseudo-absence
  (133:129), not the originally planned exact 1:1.

Features included: rainfall (7/30/90d), meteorology (7d mean + same-day
temp/dewpoint/wind), NDVI (nearest composite + anomaly), terrain
(elevation, slope), hydrology (distance-to-water).

Missing values by column:
{missing[missing > 0].to_string() if missing.sum() > 0 else 'None'}

This is the complete, final modelling dataset per the schema defined in
the Dataset Feasibility Study, Section 6, incorporating the spatial
framework (Log Entry 002), temporal framework (Log Entry 006), and
pseudo-absence methodology (Log Entry 009, 010) established throughout
this project.
"""
    with open(SUMMARY_PATH, "w") as f:
        f.write(summary)
    print(f"\nSaved summary to {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
