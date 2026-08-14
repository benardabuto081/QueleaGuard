from pathlib import Path
import pandas as pd

PA_PATH = Path("data/processed/pseudo_absences_final.csv")

print("=" * 80)
print("QueleaGuard - PA DATE PARSING MICRO-DIAGNOSTIC")
print("=" * 80)

df = pd.read_csv(PA_PATH)

print(f"\nRows: {len(df)}")

raw = df["eventDate"].astype(str).str.strip()

print("\n=== RAW DATE EXAMPLES ===")
for value in raw.head(20):
    print(repr(value))

print("\n=== PARSER TEST 1: format='mixed' ===")
parsed_mixed = pd.to_datetime(raw, format="mixed", errors="coerce", utc=True)

print(f"Parsed: {parsed_mixed.notna().sum()}")
print(f"Failed: {parsed_mixed.isna().sum()}")

print("\nFailed examples:")
for value in raw[parsed_mixed.isna()].head(20):
    print(repr(value))

print("\n=== PARSER TEST 2: DATE-ONLY NORMALIZATION ===")
date_only = raw.str[:10]
parsed_date_only = pd.to_datetime(date_only, format="%Y-%m-%d", errors="coerce")

print(f"Parsed: {parsed_date_only.notna().sum()}")
print(f"Failed: {parsed_date_only.isna().sum()}")

print("\n=== COMPARISON ===")
comparison = pd.DataFrame({
    "original": raw.head(20),
    "mixed": parsed_mixed.head(20).astype(str),
    "date_only": parsed_date_only.head(20).astype(str),
})

print(comparison.to_string(index=False))

print("\n=== DATE-ONLY RANGE ===")
valid = parsed_date_only.dropna()

print(f"Minimum: {valid.min()}")
print(f"Maximum: {valid.max()}")
print(f"Unique dates: {valid.dt.date.nunique()}")

print("\nDiagnostic complete.")
print("NO FILES WERE MODIFIED.")
