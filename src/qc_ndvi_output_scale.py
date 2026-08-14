import pandas as pd

path = "data/processed/ndvi_features_pseudo_absence.csv"

df = pd.read_csv(path)

print("=" * 80)
print("QueleaGuard - NDVI OUTPUT SCALE QC")
print("=" * 80)

print("\n=== COLUMNS ===")
print(df.columns.tolist())

print("\n=== NDVI SUMMARY ===")
print(df["ndvi"].describe())

print("\n=== FIRST 20 NDVI VALUES ===")
print(df[["grid_cell_id", "eventDate", "ndvi", "ndvi_aligned_date",
          "ndvi_temporal_distance_days"]].head(20).to_string(index=False))

print("\n=== VALUE RANGE ===")
print("Minimum:", df["ndvi"].min())
print("Maximum:", df["ndvi"].max())
print("Median: ", df["ndvi"].median())

print("\n=== SCALE DIAGNOSTIC ===")

median = df["ndvi"].median()

if 0.01 <= median <= 1:
    print("PASS: NDVI appears to be on the expected [-1, 1] scale.")
elif 0.00001 <= median <= 0.001:
    print("WARNING: NDVI appears approximately 10,000x too small.")
    print("Likely double-scaling / incorrect scale factor.")
else:
    print("REVIEW: NDVI scale is unusual and requires inspection.")

print("\n=== QC COMPLETE ===")
