"""
Milestone 3.3 - Quantify the exact impact of the MODIS NDVI temporal
boundary (Feb 2000 onward) on the candidate modelling dataset.

Uses the grid-joined occurrence dataset (Milestone 3.2) as the relevant
pool, since unmatched records are already excluded from modelling
consideration for spatial reasons.

Output: reports/milestone_3_3_temporal_boundary_impact.txt
"""

import pandas as pd

df = pd.read_csv("data/processed/occurrences_with_grid_cell.csv")

matched = df[df["grid_cell_id"].notna()].copy()
print(f"Total records matched to analysis grid (Milestone 3.2): {len(matched)}")

matched["year"] = pd.to_numeric(matched["year"], errors="coerce")

# MODIS NDVI operational start: February 2000
post_modis = matched[matched["year"] >= 2000]
pre_modis = matched[matched["year"] < 2000]
undated = matched[matched["year"].isna()]

print(f"\nRecords on/after 2000 (feature-complete modelling candidates): {len(post_modis)}")
print(f"Records before 2000 (excluded from modelling, retained for EDA): {len(pre_modis)}")
print(f"Records with missing/unparseable year: {len(undated)}")

pct_retained = 100 * len(post_modis) / len(matched)
pct_excluded = 100 * len(pre_modis) / len(matched)

print(f"\nPercentage retained for modelling dataset: {pct_retained:.1f}%")
print(f"Percentage excluded (pre-2000): {pct_excluded:.1f}%")

print("\nExcluded (pre-2000) records detail:")
print(pre_modis[["year", "decimalLatitude", "decimalLongitude", "eventDate"]].sort_values("year").to_string(index=False))

summary = f"""Milestone 3.3 - MODIS NDVI Temporal Boundary Impact
=======================================================

Candidate pool: {len(matched)} occurrence records matched to the analysis grid (Milestone 3.2)

Records retained for feature-complete modelling dataset (year >= 2000): {len(post_modis)} ({pct_retained:.1f}%)
Records excluded from modelling dataset, retained for EDA/historical context (year < 2000): {len(pre_modis)} ({pct_excluded:.1f}%)
Records with missing/unparseable year: {len(undated)}

This exclusion reflects a data availability constraint (MODIS NDVI operational start,
February 2000), not a data quality judgement. Pre-2000 records remain valid historical
occurrence evidence and will continue to appear in exploratory analyses, temporal
summaries, and project documentation.
"""

with open("reports/milestone_3_3_temporal_boundary_impact.txt", "w") as f:
    f.write(summary)
print("\nSaved to reports/milestone_3_3_temporal_boundary_impact.txt")
