"""
Milestone 3.8 (final) - Compute distance-to-water for all 328 grid cells,
combining HydroRIVERS (rivers, clipped to analysis extent) and Lake
Victoria's boundary (from OpenStreetMap).

Output: data/processed/hydrology_features.csv
        reports/milestone_3_8_hydrology_extraction_summary.txt
"""

import geopandas as gpd
import pandas as pd

RIVERS_PATH = "data/external/hydrosheds_cache/HydroRIVERS_v10_af.gdb.zip"
LAKE_PATH = "data/external/lake_victoria.geojson"
GRID_PATH = "data/processed/analysis_grid.geojson"
OUTPUT_PATH = "data/processed/hydrology_features.csv"
SUMMARY_PATH = "reports/milestone_3_8_hydrology_extraction_summary.txt"
UTM_CRS = "EPSG:32736"
WGS84_CRS = "EPSG:4326"


def main():
    grid = gpd.read_file(GRID_PATH)
    minx, miny, maxx, maxy = grid.total_bounds
    print(f"Analysis extent: ({minx:.3f}, {miny:.3f}) to ({maxx:.3f}, {maxy:.3f})")

    # Read HydroRIVERS with a bounding-box filter pushed down to the file
    # read itself (avoids loading the entire Africa-wide network into memory).
    print("Reading HydroRIVERS (clipped to analysis extent via bbox filter)...")
    rivers = gpd.read_file(RIVERS_PATH, bbox=(minx, miny, maxx, maxy))
    print(f"River reaches within extent: {len(rivers)}")

    print("Reading Lake Victoria boundary...")
    lake = gpd.read_file(LAKE_PATH)

    # Reproject everything to metric UTM for accurate distance calculation
    rivers_utm = rivers.to_crs(UTM_CRS)
    lake_utm = lake.to_crs(UTM_CRS)
    grid_utm = grid.to_crs(UTM_CRS)

    # Combine rivers + lake into one set of water geometries
    water_geoms = list(rivers_utm.geometry) + list(lake_utm.geometry)
    water_union = gpd.GeoSeries(water_geoms, crs=UTM_CRS).union_all()
    print(f"Combined water features: {len(water_geoms)}")

    grid_utm["dist_to_water_m"] = grid_utm.geometry.centroid.distance(water_union)

    results_df = grid_utm[["grid_cell_id", "dist_to_water_m"]].copy()
    results_df["dist_to_water_m"] = results_df["dist_to_water_m"].round(1)
    results_df.to_csv(OUTPUT_PATH, index=False)

    print(f"\nExtracted distance-to-water for {len(results_df)} grid cells.")
    print(f"Saved to {OUTPUT_PATH}")
    print("\nSample results:")
    print(results_df.head(10).to_string(index=False))
    print("\nDistance statistics:")
    print(results_df["dist_to_water_m"].describe())

    summary = f"""Milestone 3.8 - Hydrology (Distance-to-Water) Feature Extraction Summary
=============================================================================

Grid cells processed: {len(results_df)}
Sources combined: HydroRIVERS Africa ({len(rivers)} reaches within analysis
extent) + Lake Victoria boundary (OpenStreetMap, {len(lake)} feature)

Distance computed from each grid cell centroid to the nearest water
feature (river or lake), in meters, via projected CRS (EPSG:32736, UTM 36S).

Distance statistics (meters):
{results_df['dist_to_water_m'].describe().to_string()}
"""
    with open(SUMMARY_PATH, "w") as f:
        f.write(summary)
    print(f"\nSaved summary to {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
