"""
Milestone 3.9 (fixed) - Build the candidate pseudo-absence pool.
Same logic as before, but thinning uses a shuffle + cumcount mask instead
of groupby.apply, avoiding a pandas version-dependent column-dropping issue.
"""

import pandas as pd
import geopandas as gpd

POOL_PATH = "data/raw/gbif_all_species_effort_pool.csv"
GRID_PATH = "data/processed/analysis_grid.geojson"
OUTPUT_PATH = "data/processed/pseudo_absence_pool.csv"
SUMMARY_PATH = "reports/milestone_3_9_pseudo_absence_pool_summary.txt"

MAX_PER_CELL = 5


def main():
    df = pd.read_csv(POOL_PATH)
    print(f"Raw effort pool: {len(df)} records")

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
    print(f"Columns present after join: {list(joined.columns)}")

    # Shuffle, then keep only the first MAX_PER_CELL rows per grid cell -
    # avoids groupby.apply's column-dropping behavior entirely.
    joined_shuffled = joined.sample(frac=1, random_state=42).reset_index(drop=True)
    joined_shuffled["_rank_in_cell"] = joined_shuffled.groupby("grid_cell_id").cumcount()
    thinned = joined_shuffled[joined_shuffled["_rank_in_cell"] < MAX_PER_CELL].drop(columns=["_rank_in_cell"])

    print(f"After spatial thinning (max {MAX_PER_CELL} per cell): {len(thinned)} records")
    print(f"Unique grid cells represented in thinned pool: {thinned['grid_cell_id'].nunique()}")

    output_cols = ["key", "scientificName", "decimalLatitude", "decimalLongitude",
                    "eventDate", "year", "grid_cell_id", "within_scheme_boundary"]
    thinned_df = thinned[output_cols].copy()
    thinned_df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved candidate pseudo-absence pool to {OUTPUT_PATH}")

    summary = f"""Milestone 3.9 - Pseudo-Absence Candidate Pool Summary
==========================================================

Raw effort pool (all-species GBIF query, capped at 3000): 3000
After excluding Quelea quelea: {len(df)}
After year >= 2000 filter (matches modelling dataset temporal boundary, Log Entry 006): {len(df)}
After spatial join to analysis grid (Log Entry 002): {len(joined)}
After spatial thinning (max {MAX_PER_CELL} per grid cell): {len(thinned_df)}

Unique grid cells represented: {thinned_df['grid_cell_id'].nunique()} of 328 total
Unique species contributing to the effort proxy: {thinned_df['scientificName'].nunique()}

This pool represents locations/dates where birding effort is evidenced
via other-species GBIF records, but Quelea quelea was not recorded -
the approximate Target-Group Background candidate set, per Log Entry 009.

Next step: sample the final pseudo-absence set from this pool at the
target presence:pseudo-absence ratio.
"""
    with open(SUMMARY_PATH, "w") as f:
        f.write(summary)
    print(f"Saved summary to {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
