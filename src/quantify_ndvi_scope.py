"""
Milestone 3.6 (scoping) - Determine unique grid cells needed for MODIS
NDVI extraction, and confirm the request strategy: one AppEEARS point
task covering all unique cells' full MODIS history (2000-present), rather
than per-record requests.
"""

import pandas as pd

df = pd.read_csv("data/processed/occurrences_with_grid_cell.csv")
df["year"] = pd.to_numeric(df["year"], errors="coerce")
candidates = df[(df["year"] >= 2000) & (df["grid_cell_id"].notna())].copy()

unique_cells = candidates["grid_cell_id"].nunique()
print(f"Modelling-candidate records: {len(candidates)}")
print(f"Unique grid cells needed: {unique_cells}")
print(f"\nRecords per cell (top 10):")
print(candidates["grid_cell_id"].value_counts().head(10))

print(f"\nStrategy: 1 AppEEARS point task, {unique_cells} coordinates, "
      f"full MODIS record (2000-01-01 to present) - not one task per record.")
