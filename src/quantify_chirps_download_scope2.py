"""
Diagnostic (fixed) - truncate eventDate to date-only before parsing,
avoiding mixed-format inference issues, then re-quantify CHIRPS download scope.
"""

import pandas as pd
from datetime import timedelta

df = pd.read_csv("data/processed/occurrences_with_grid_cell.csv")
df["year"] = pd.to_numeric(df["year"], errors="coerce")
candidates = df[(df["year"] >= 2000) & (df["grid_cell_id"].notna())].copy()

# Take just the first 10 characters (YYYY-MM-DD) before parsing
candidates["eventDate_clean"] = candidates["eventDate"].str[:10]
candidates["eventDate_parsed"] = pd.to_datetime(candidates["eventDate_clean"], format="%Y-%m-%d", errors="coerce")

print(f"Candidates: {len(candidates)}")
print(f"Successfully parsed this time: {candidates['eventDate_parsed'].notna().sum()}")
print(f"Still failed: {candidates['eventDate_parsed'].isna().sum()}")

candidates = candidates.dropna(subset=["eventDate_parsed"])

unique_dates = set()
for obs_date in candidates["eventDate_parsed"]:
    for days_back in range(91):
        unique_dates.add((obs_date - timedelta(days=days_back)).date())

print(f"\nUnique calendar days needed across all 90-day windows: {len(unique_dates)}")
print(f"Estimated download size at ~3.2MB/file (compressed): {len(unique_dates) * 3.2 / 1000:.1f} GB")

years_needed = sorted(set(d.year for d in unique_dates))
print(f"Years spanned: {years_needed}")
