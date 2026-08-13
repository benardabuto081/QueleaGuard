"""
Diagnose month-level temporal skew in the pseudo-absence effort-proxy
pool - a possible unaddressed analog of the year-level skew already
fixed in fetch_effort_pool.py (Log Entry 009).
"""

import pandas as pd

raw = pd.read_csv("data/raw/gbif_all_species_effort_pool.csv")
pool = pd.read_csv("data/processed/pseudo_absence_pool.csv")
final_pa = pd.read_csv("data/processed/pseudo_absences_final.csv")

print("=== Month distribution: RAW effort pool (pre-thinning) ===")
print(raw["month"].value_counts().sort_index())
print(f"Total: {len(raw)}")

print("\n=== Month distribution: THINNED candidate pool ===")
if "month" in pool.columns:
    print(pool["month"].value_counts().sort_index())
else:
    pool["eventDate"] = pd.to_datetime(pool["eventDate"], errors="coerce")
    print(pool["eventDate"].dt.month.value_counts().sort_index())
print(f"Total: {len(pool)}")

print("\n=== Month distribution: FINAL sampled pseudo-absences ===")
final_pa["eventDate"] = pd.to_datetime(final_pa["eventDate"], errors="coerce")
print(final_pa["eventDate"].dt.month.value_counts().sort_index())
print(f"Total: {len(final_pa)}")

print("\n=== Per-year record count in RAW pool (was the 150/year cap actually hit?) ===")
print(raw.groupby("year").size().sort_index())

print("\n=== Per-year, per-month breakdown in RAW pool (first 5 years, to see if truncation is visible) ===")
sample_years = sorted(raw["year"].dropna().unique())[:5]
for yr in sample_years:
    yr_data = raw[raw["year"] == yr]
    print(f"\nYear {int(yr)} (n={len(yr_data)}):")
    print(yr_data["month"].value_counts().sort_index().to_dict())
