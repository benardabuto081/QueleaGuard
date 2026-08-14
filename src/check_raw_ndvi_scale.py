import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

NDVI_DIR = ROOT / "data" / "external" / "appeears_ndvi_pa_v2_gap_45cells"

csv_file = sorted(NDVI_DIR.glob("*.csv"))[0]

df = pd.read_csv(csv_file)

col = "MOD13Q1_061__250m_16_days_NDVI"

x = pd.to_numeric(df[col], errors="coerce")

print("=" * 80)
print("QueleaGuard - RAW APPEEARS NDVI SCALE CHECK")
print("=" * 80)

print("\n=== RAW NDVI SUMMARY ===")
print(x.describe())

print("\n=== FIRST 20 RAW VALUES ===")
print(x.head(20).to_string(index=False))

print("\n=== UNIQUE SAMPLE VALUES ===")
print(x.dropna().drop_duplicates().head(30).to_list())

print("\n=== RAW RANGE ===")
print("Minimum:", x.min())
print("Maximum:", x.max())
print("Median: ", x.median())

print("\n=== SCALE INTERPRETATION ===")

if x.max() <= 1.0 and x.min() >= -1.0:
    print("Raw AppEEARS values are already approximately in [-1, 1].")
    print("DO NOT apply the 0.0001 MODIS scale factor again.")
elif x.max() > 100:
    print("Raw values appear to be integer-scaled MODIS values.")
    print("A 0.0001 scale factor may be appropriate.")
else:
    print("Raw value scale needs further inspection.")

print("\n" + "=" * 80)
