"""
Diagnostic - investigate why zero pseudo-absences fall within the Ahero
scheme boundary, despite presence data having records there.
"""

import pandas as pd

pool = pd.read_csv("data/processed/pseudo_absence_pool.csv")
raw_joined_count = pool["within_scheme_boundary"].sum()
print(f"Pseudo-absence candidate pool (196 records): "
      f"{raw_joined_count} within scheme boundary, {len(pool) - raw_joined_count} in buffer only")

# Check the grid itself: how many of the 328 cells are actually within
# the scheme boundary vs. buffer-only?
import geopandas as gpd
grid = gpd.read_file("data/processed/analysis_grid.geojson")
print(f"\nGrid cells within scheme boundary: {grid['within_scheme_boundary'].sum()} of {len(grid)} total")

# And within the RAW (pre-thinning) effort pool, before any sampling:
raw = pd.read_csv("data/raw/gbif_all_species_effort_pool.csv")
print(f"\nRaw effort pool size: {len(raw)}")
