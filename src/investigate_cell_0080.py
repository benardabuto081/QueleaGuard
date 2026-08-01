"""
Milestone 3.2 (continued) - Investigate the heavy concentration of
occurrence records in cell_0080, to determine whether it reflects genuine
ecological signal or observation-effort/duplicate artifacts.
"""

import pandas as pd

df = pd.read_csv("data/processed/occurrences_with_grid_cell.csv")
cell = df[df["grid_cell_id"] == "cell_0080"]

print(f"Total records in cell_0080: {len(cell)}")
print(f"Is this cell within the Ahero scheme boundary? {cell['within_scheme_boundary'].iloc[0]}")
print()

print("Unique lat/lon coordinates in this cell:")
print(cell[["decimalLatitude", "decimalLongitude"]].drop_duplicates())
print()

print("Date range in this cell:")
print(f"  Earliest: {cell['eventDate'].min()}")
print(f"  Latest: {cell['eventDate'].max()}")
print()

print("Unique dates (how many distinct days were birds actually seen here):")
print(f"  {cell['eventDate'].nunique()} unique dates across {len(cell)} records")
print()

print("Records per unique observer:")
print(cell["recordedBy"].value_counts().head(10))
print()

print("Source dataset breakdown:")
print(cell["datasetKey"].value_counts())
