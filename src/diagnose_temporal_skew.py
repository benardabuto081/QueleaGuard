"""
Diagnostic - investigate why the pseudo-absence sample is concentrated
in 2024-2026 despite the candidate pool covering year >= 2000.
"""

import pandas as pd

pool = pd.read_csv("data/processed/pseudo_absence_pool.csv")
raw = pd.read_csv("data/raw/gbif_all_species_effort_pool.csv")

print("Year distribution in the FULL raw effort pool (3000 records, before thinning):")
print(raw["year"].value_counts().sort_index())

print("\nYear distribution in the THINNED candidate pool (352 records):")
print(pool["year"].value_counts().sort_index())

print("\nFor comparison, presence record year distribution (from Milestone 2.1 findings):")
occ = pd.read_csv("data/processed/occurrences_with_grid_cell.csv")
occ["year"] = pd.to_numeric(occ["year"], errors="coerce")
print(occ[occ["year"] >= 2000]["year"].value_counts().sort_index())
