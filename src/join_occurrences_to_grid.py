"""
Milestone 3.2 - Join GBIF occurrence records onto the analysis grid.

Determines which grid cell (if any) each occurrence record falls into,
using the precise analysis extent boundary (not the rectangular
approximation used in earlier bounding-box queries).

Output: data/processed/occurrences_with_grid_cell.csv
        reports/milestone_3_2_occurrence_grid_join_summary.txt
"""

import geopandas as gpd
import pandas as pd

OCCURRENCES_PATH = "data/raw/gbif_kisumu_county_raw.csv"
GRID_PATH = "data/processed/analysis_grid.geojson"
OUTPUT_PATH = "data/processed/occurrences_with_grid_cell.csv"
SUMMARY_PATH = "reports/milestone_3_2_occurrence_grid_join_summary.txt"


def main():
    # Load occurrence records and convert to a GeoDataFrame of points
    occ_df = pd.read_csv(OCCURRENCES_PATH)
    occ_gdf = gpd.GeoDataFrame(
        occ_df,
        geometry=gpd.points_from_xy(occ_df["decimalLongitude"], occ_df["decimalLatitude"]),
        crs="EPSG:4326",
    )
    print(f"Loaded {len(occ_gdf)} occurrence records.")

    # Load the analysis grid
    grid_gdf = gpd.read_file(GRID_PATH)
    print(f"Loaded {len(grid_gdf)} grid cells.")

    # Spatial join: for each occurrence point, find which grid cell (if any) contains it
    joined = gpd.sjoin(occ_gdf, grid_gdf, how="left", predicate="within")

    matched = joined["grid_cell_id"].notna().sum()
    unmatched = joined["grid_cell_id"].isna().sum()
    print(f"\nRecords matched to a grid cell: {matched}")
    print(f"Records outside the analysis extent (no matching cell): {unmatched}")

    within_scheme = joined[joined["within_scheme_boundary"] == True]
    print(f"Records falling specifically within the Ahero scheme boundary cells: {len(within_scheme)}")

    # Records per grid cell (top occupied cells)
    cell_counts = joined["grid_cell_id"].value_counts().head(10)
    print("\nTop 10 grid cells by occurrence count:")
    print(cell_counts)

    # Save the joined dataset (drop the geometry/index columns from the join, keep the essentials)
    output_df = joined.drop(columns=["geometry", "index_right"], errors="ignore")
    output_df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved joined dataset to {OUTPUT_PATH}")

    summary = f"""Milestone 3.2 - Occurrence-to-Grid Join Summary
===================================================

Source occurrences: {OCCURRENCES_PATH} (161 raw GBIF/eBird records, Milestone 2.1)
Analysis grid: {GRID_PATH} (328 cells, Milestone 3.1)

Records matched to a grid cell (within analysis extent): {matched}
Records outside the analysis extent: {unmatched}
Records within Ahero scheme boundary cells specifically: {len(within_scheme)}

Occupied grid cells: {joined['grid_cell_id'].nunique()} of 328 total cells contain at least one occurrence record.

Output file: {OUTPUT_PATH}
"""
    with open(SUMMARY_PATH, "w") as f:
        f.write(summary)
    print(f"Saved summary to {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
