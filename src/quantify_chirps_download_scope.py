"""
Milestone 3.4 (diagnostic) - Quantify the number of unique CHIRPS daily
files required to cover all 90-day antecedent windows across the 133
modelling-candidate records, before committing to a download strategy.
"""

import pandas as pd
from datetime import timedelta

df = pd.read_csv("data/processed/occurrences_with_grid_cell.csv")
df["year"] = pd.to_numeric(df["year"], errors="coerce")
candidates = df[(df["year"] >= 2000) & (df["grid_cell_id"].notna())].copy()
candidates["eventDate"] = pd.to_datetime(candidates["eventDate"], errors="coerce")
candidates = candidates.dropna(subset=["eventDate"])

unique_dates = set()
for obs_date in candidates["eventDate"]:
    for days_back in range(91):
        unique_dates.add((obs_date - timedelta(days=days_back)).date())

print(f"Candidate records: {len(candidates)}")
print(f"Unique calendar days needed across all 90-day windows: {len(unique_dates)}")
print(f"Estimated download size at ~3.2MB/file (compressed): {len(unique_dates) * 3.2 / 1000:.1f} GB")

years_needed = sorted(set(d.year for d in unique_dates))
print(f"\nYears spanned: {years_needed}")
