"""
Diagnostic - investigate why eventDate parsing yields far fewer candidates
than Milestone 3.3's confirmed 133.
"""

import pandas as pd

df = pd.read_csv("data/processed/occurrences_with_grid_cell.csv")
df["year"] = pd.to_numeric(df["year"], errors="coerce")
candidates = df[(df["year"] >= 2000) & (df["grid_cell_id"].notna())].copy()
print(f"Candidates by year/grid_cell_id filter alone: {len(candidates)}")

print("\nSample raw eventDate values:")
print(candidates["eventDate"].head(10).tolist())

parsed = pd.to_datetime(candidates["eventDate"], errors="coerce")
print(f"\nSuccessfully parsed: {parsed.notna().sum()}")
print(f"Failed to parse (NaT): {parsed.isna().sum()}")

print("\nSample values that FAILED to parse:")
failed_mask = parsed.isna()
print(candidates.loc[failed_mask, "eventDate"].head(10).tolist())
