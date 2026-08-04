"""
Milestone 3.9 (validation check) - Compare the 4 scheme-boundary grid
cells' environmental characteristics (elevation, slope, distance-to-water)
against the full 328-cell grid, to verify whether the scheme is
environmentally represented elsewhere in the analysis extent (supporting
interpolation) or environmentally distinct (which would undermine Option 1).

Also checks whether the scheme cells fall within the 20-cell set with
full NDVI time series coverage (Milestone 3.6).
"""

import pandas as pd

terrain = pd.read_csv("data/processed/terrain_features.csv")
hydrology = pd.read_csv("data/processed/hydrology_features.csv")
grid_env = terrain.merge(hydrology, on="grid_cell_id")

import geopandas as gpd
grid = gpd.read_file("data/processed/analysis_grid.geojson")
scheme_cells = grid[grid["within_scheme_boundary"] == True]["grid_cell_id"].tolist()
print(f"Scheme-boundary grid cells: {scheme_cells}")

scheme_env = grid_env[grid_env["grid_cell_id"].isin(scheme_cells)]
rest_env = grid_env[~grid_env["grid_cell_id"].isin(scheme_cells)]

print("\n" + "=" * 60)
print("SCHEME-BOUNDARY CELLS (n=4)")
print("=" * 60)
print(scheme_env[["grid_cell_id", "elevation_m", "slope_deg", "dist_to_water_m"]].to_string(index=False))

print("\n" + "=" * 60)
print("FULL GRID STATISTICS (n=328) FOR COMPARISON")
print("=" * 60)
print(grid_env[["elevation_m", "slope_deg", "dist_to_water_m"]].describe())

print("\n" + "=" * 60)
print("REST-OF-GRID STATISTICS (n=324, excluding scheme cells)")
print("=" * 60)
print(rest_env[["elevation_m", "slope_deg", "dist_to_water_m"]].describe())

# Check where each scheme cell's values fall within the full grid's percentile range
print("\n" + "=" * 60)
print("PERCENTILE POSITION OF SCHEME CELLS WITHIN FULL GRID RANGE")
print("=" * 60)
for _, row in scheme_env.iterrows():
    elev_pct = (grid_env["elevation_m"] < row["elevation_m"]).mean() * 100
    slope_pct = (grid_env["slope_deg"] < row["slope_deg"]).mean() * 100
    dist_pct = (grid_env["dist_to_water_m"] < row["dist_to_water_m"]).mean() * 100
    print(f"{row['grid_cell_id']}: elevation at {elev_pct:.0f}th percentile, "
          f"slope at {slope_pct:.0f}th percentile, dist_to_water at {dist_pct:.0f}th percentile")

# Check NDVI coverage overlap
print("\n" + "=" * 60)
print("NDVI COVERAGE CHECK")
print("=" * 60)
ndvi_history = pd.read_csv("data/external/appeears_ndvi_full_history.csv")
ndvi_cells = set(ndvi_history["ID"].unique())
overlap = set(scheme_cells) & ndvi_cells
print(f"Scheme cells with full NDVI time series available: {overlap if overlap else 'NONE'}")
