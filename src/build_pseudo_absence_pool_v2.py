"""
Milestone 4.4 (correction, cont.) - Rebuild the thinned pseudo-absence
candidate pool from the corrected, month-stratified effort pool. Adds the
presence-conflict exclusion safeguard flagged in Log Entry 013: any
effort-proxy record sharing a (grid_cell_id, date) pair with a confirmed
Quelea quelea presence record is excluded before thinning, preventing
recurrence of the TGB assumption violation found in Milestone 3.11.

Backs up the v1 (month-biased) pool before overwriting.

Output: data/processed/pseudo_absence_pool.csv (rebuilt)
        data/processed/pseudo_absence_pool_v1_month_skewed.csv (backup)
"""

import os
import shutil
import pandas as pd
import geopandas as gpd

RAW_POOL_PATH = "data/raw/gbif_all_species_effort_pool.csv"
OCCURRENCES_PATH = "data/processed/occurrences_with_grid_cell.csv"
GRID_PATH = "data/processed/analysis_grid.geojson"
OUTPUT_PATH = "data/processed/pseudo_absence_pool.csv"
BACKUP_PATH = "data/processed/pseudo_absence_pool_v1_month_skewed.csv"
SUMMARY_PATH = "reports/milestone_4_4_pseudo_absence_pool_v2_summary.txt"

MAX_PER_CELL = 5


def main():
    if os.path.exists(OUTPUT_PATH) and not os.path.exists(BACKUP_PATH):
        shutil.copy(OUTPUT_PATH, BACKUP_PATH)
        print(f"Backed up v1 pool to {BACKUP_PATH}")

    df = pd.read_csv(RAW_POOL_PATH)
    print(f"Raw (rebuilt) effort pool: {len(df)} records")

    df = df[~df["scientificName"].str.contains("Quelea quelea", na=False)].copy()
    print(f"After excluding Quelea quelea: {len(df)} records")

    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df.dropna(subset=["decimalLatitude", "decimalLongitude", "eventDate"])
    df = df[df["year"] >= 2000]
    print(f"After year >= 2000 filter: {len(df)} records")

    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df["decimalLongitude"], df["decimalLatitude"]), crs="EPSG:4326"
    )
    grid = gpd.read_file(GRID_PATH)
    joined = gpd.sjoin(gdf, grid, how="inner", predicate="within")
    print(f"After spatial join to analysis grid: {len(joined)} records")

    # --- Presence-conflict exclusion safeguard (Log Entry 013 follow-up) ---
    joined["obs_date"] = pd.to_datetime(joined["eventDate"], errors="coerce").dt.date

    occ = pd.read_csv(OCCURRENCES_PATH)
    occ["year"] = pd.to_numeric(occ["year"], errors="coerce")
    presences = occ[(occ["year"] >= 2000) & (occ["grid_cell_id"].notna())].copy()
    presences["obs_date"] = pd.to_datetime(presences["eventDate"], errors="coerce").dt.date
    presence_pairs = set(zip(presences["grid_cell_id"], presences["obs_date"]))

    pre_conflict_count = len(joined)
    joined["conflict_key"] = list(zip(joined["grid_cell_id"], joined["obs_date"]))
    joined = joined[~joined["conflict_key"].isin(presence_pairs)].copy()
    print(f"After excluding (cell, date) pairs matching a presence record: {len(joined)} "
          f"({pre_conflict_count - len(joined)} excluded)")

    joined_shuffled = joined.sample(frac=1, random_state=42).reset_index(drop=True)
    joined_shuffled["_rank_in_cell"] = joined_shuffled.groupby("grid_cell_id").cumcount()
    thinned = joined_shuffled[joined_shuffled["_rank_in_cell"] < MAX_PER_CELL].drop(columns=["_rank_in_cell"])

    print(f"After spatial thinning (max {MAX_PER_CELL} per cell): {len(thinned)} records")
    print(f"Unique grid cells represented: {thinned['grid_cell_id'].nunique()}")

    output_cols = ["key", "scientificName", "decimalLatitude", "decimalLongitude",
                    "eventDate", "year", "grid_cell_id", "within_scheme_boundary"]
    thinned_df = thinned[output_cols].copy()
    thinned_df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved corrected candidate pool to {OUTPUT_PATH}")

    print(f"\nMonth distribution in corrected candidate pool:")
    thinned_df["_month"] = pd.to_datetime(thinned_df["eventDate"], errors="coerce").dt.month
    print(thinned_df["_month"].value_counts().sort_index())

    summary = f"""Milestone 4.4 - Corrected Pseudo-Absence Candidate Pool
==========================================================

Rebuilt from month-stratified effort pool (fetch_effort_pool_v2_month_stratified.py),
correcting the severe January-concentration bug (96.8% of original pseudo-absences
fell in Jan/Feb). Root cause: original fetch_effort_pool.py queried GBIF by year
only, capping at 150/year, which combined with GBIF's undocumented default result
ordering to produce near-total January truncation in several years.

Also adds the presence-conflict exclusion safeguard flagged in Log Entry 013:
{pre_conflict_count - len(joined)} effort-proxy records were excluded because
they shared a (grid_cell_id, date) pair with a confirmed presence record.

Raw rebuilt effort pool: {len(df) + (pre_conflict_count - len(joined))} (approx, pre-filters)
After year >= 2000 filter and spatial join: {pre_conflict_count}
After presence-conflict exclusion: {len(joined)}
After spatial thinning (max {MAX_PER_CELL}/cell): {len(thinned_df)}

v1 (biased) pool backed up to: {BACKUP_PATH}
"""
    with open(SUMMARY_PATH, "w") as f:
        f.write(summary)
    print(f"\nSaved summary to {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
