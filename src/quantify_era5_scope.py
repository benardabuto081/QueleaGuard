"""
Milestone 3.5 (scoping) - Determine unique year-month combinations needed
for ERA5-Land meteorology extraction (7-day window, per Log Entry 006),
to plan an efficient batched CDS API request strategy.
"""

import pandas as pd
from datetime import timedelta

df = pd.read_csv("data/processed/occurrences_with_grid_cell.csv")
df["year"] = pd.to_numeric(df["year"], errors="coerce")
candidates = df[(df["year"] >= 2000) & (df["grid_cell_id"].notna())].copy()
candidates["eventDate_clean"] = candidates["eventDate"].str[:10]
candidates["eventDate_parsed"] = pd.to_datetime(
    candidates["eventDate_clean"], format="%Y-%m-%d", errors="coerce"
)
candidates = candidates.dropna(subset=["eventDate_parsed"])

print(f"Modelling-candidate records: {len(candidates)}")

unique_dates = set()
for obs_date in candidates["eventDate_parsed"]:
    for days_back in range(7):  # 7-day window per Log Entry 006, much smaller than CHIRPS's 90
        unique_dates.add((obs_date - timedelta(days=days_back)).date())

print(f"Unique calendar days needed (7-day windows): {len(unique_dates)}")

year_months = sorted(set((d.year, d.month) for d in unique_dates))
print(f"Unique (year, month) combinations needed: {len(year_months)}")
print("\nList of year-months:")
for ym in year_months:
    days_in_this_month = sorted(d.day for d in unique_dates if (d.year, d.month) == ym)
    print(f"  {ym[0]}-{ym[1]:02d}: {len(days_in_this_month)} days needed")
