"""
Diagnose why most eventDate values in the corrected pseudo-absence sample
fail to parse into a single month - likely GBIF date-interval strings
(e.g. "2016-01-15/2016-01-20") rather than single ISO dates, a known GBIF
data quality characteristic already documented for a subset of presence
records. Need to confirm before trusting the month-distribution QC check.
"""

import pandas as pd

sampled = pd.read_csv("data/processed/pseudo_absences_final.csv")
print(f"Total records: {len(sampled)}")

parsed = pd.to_datetime(sampled["eventDate"], errors="coerce")
print(f"Successfully parsed as single date: {parsed.notna().sum()}")
print(f"Failed to parse: {parsed.isna().sum()}")

print("\nSample of RAW eventDate values that failed to parse:")
failed = sampled[parsed.isna()]
print(failed["eventDate"].head(20).to_string(index=False))

print("\nAre failures all date-interval format (contain '/')?")
print(failed["eventDate"].astype(str).str.contains("/").value_counts())
