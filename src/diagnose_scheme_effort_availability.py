"""
Diagnostic (continued) - check whether ANY effort-proxy records exist
within the scheme boundary before spatial thinning removed them.
"""

import pandas as pd
import geopandas as gpd

raw = pd.read_csv("data/raw/gbif_all_species_effort_pool.csv")
raw = raw.dropna(subset=["decimalLatitude", "decimalLongitude"])

gdf = gpd.GeoDataFrame(
    raw, geometry=gpd.points_from_xy(raw["decimalLongitude"], raw["decimalLatitude"]), crs="EPSG:4326"
)
grid = gpd.read_file("data/processed/analysis_grid.geojson")
joined = gpd.sjoin(gdf, grid, how="inner", predicate="within")

within_scheme = joined[joined["within_scheme_boundary"] == True]
print(f"Total effort records joined to grid: {len(joined)}")
print(f"Effort records within scheme boundary (before thinning): {len(within_scheme)}")

if len(within_scheme) > 0:
    print("\nThese exist but were excluded by thinning. Sample:")
    print(within_scheme[["scientificName", "year", "grid_cell_id"]].head(10))
else:
    print("\nNo effort-proxy records exist within the scheme boundary in this pool at all.")
