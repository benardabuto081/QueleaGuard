"""
Milestone 3.10 - Assemble the final modelling dataset from all extracted
feature tables. NDVI join deferred pending completion of the pseudo-
absence NDVI gap-fill task (Milestone 3.9); all other features included.

Output: data/processed/modelling_dataset_partial.csv (without NDVI)
        reports/milestone_3_10_assembly_summary.txt
"""

import pandas as pd

OCCURRENCES_PATH = "data/processed/occurrences_with_grid_cell.csv"
PSEUDO_ABSENCES_PATH = "data/processed/pseudo_absences_final.csv"
RAINFALL_PATH = "data/processed/rainfall_features.csv"
METEOROLOGY_PATH = "data/processed/meteorology_features.csv"
TERRAIN_PATH = "data/processed/terrain_features.csv"
HYDROLOGY_PATH = "data/processed/hydrology_features.csv"
OUTPUT_PATH = "data/processed/modelling_dataset_partial.csv"
SUMMARY_PATH = "reports/milestone_3_10_assembly_summary.txt"


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
    print(f"Presence records: {len(presences)}")

    # --- Pseudo-absence records ---
    pa = pd.read_csv(PSEUDO_ABSENCES_PATH)
    pa = pa.rename(columns={"key": "record_key", "eventDate": "observation_date"})
    pa["observation_date"] = pa["observation_date"].astype(str).str[:10]
    pa = pa[["record_key", "grid_cell_id", "observation_date", "presence", "within_scheme_boundary"]]
    pa["record_type"] = "pseudo_absence"
    print(f"Pseudo-absence records: {len(pa)}")

    combined = pd.concat([presences, pa], ignore_index=True)
    print(f"\nCombined dataset (before feature join): {len(combined)} records")
    print(f"Presence: {(combined['presence'] == 1).sum()}, Pseudo-absence: {(combined['presence'] == 0).sum()}")

    # --- Join rainfall (per-record, matched on record_key) ---
    rainfall = pd.read_csv(RAINFALL_PATH)[["record_key", "rainfall_7d", "rainfall_30d", "rainfall_90d"]]
    combined = combined.merge(rainfall, on="record_key", how="left")

    # --- Join meteorology (per-record) ---
    met = pd.read_csv(METEOROLOGY_PATH)[
        ["record_key", "temp_mean_7d", "dewpoint_mean_7d", "wind_mean_7d",
         "temp_same_day", "dewpoint_same_day", "wind_same_day"]
    ]
    combined = combined.merge(met, on="record_key", how="left")

    # --- Join terrain (per grid cell, static) ---
    terrain = pd.read_csv(TERRAIN_PATH)
    combined = combined.merge(terrain, on="grid_cell_id", how="left")

    # --- Join hydrology (per grid cell, static) ---
    hydrology = pd.read_csv(HYDROLOGY_PATH)
    combined = combined.merge(hydrology, on="grid_cell_id", how="left")

    # NDVI placeholder - to be filled in once the pending gap-fill task completes
    combined["ndvi_nearest_composite"] = None
    combined["ndvi_anomaly"] = None

    combined.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved partial modelling dataset (NDVI pending) to {OUTPUT_PATH}")
    print(f"Total records: {len(combined)}")
    print(f"Columns: {list(combined.columns)}")

    print("\nMissing value check (excluding NDVI placeholder columns):")
    check_cols = [c for c in combined.columns if c not in ["ndvi_nearest_composite", "ndvi_anomaly"]]
    print(combined[check_cols].isna().sum()[lambda s: s > 0])

    summary = f"""Milestone 3.10 - Partial Dataset Assembly Summary (NDVI pending)
=====================================================================

Presence records: {len(presences)}
Pseudo-absence records: {len(pa)}
Total records: {len(combined)}

Features joined: rainfall (7/30/90d), meteorology (7d mean + same-day),
terrain (elevation, slope), hydrology (distance-to-water).

NDVI: pending completion of AppEEARS gap-fill task
(0889d6bb-d49a-44c5-9a41-239ee27bff4f), which covers the 43 grid cells
used by pseudo-absence records not covered by the original Milestone 3.6
NDVI extraction (which only covered presence-record cells).

This is an intermediate file - data/processed/modelling_dataset_partial.csv,
not the final modelling dataset.
"""
    with open(SUMMARY_PATH, "w") as f:
        f.write(summary)
    print(f"\nSaved summary to {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
