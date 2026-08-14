from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

NDVI_PATH = (
    ROOT
    / "data"
    / "external"
    / "appeears_ndvi_pa_v2_gap_45cells"
    / "queleaguard-ndvi-pa-v2-gap-45cells-MOD13Q1-061-results.csv"
)

PA_PATH = (
    ROOT
    / "data"
    / "processed"
    / "pseudo_absences_final.csv"
)

print("=" * 80)
print("QueleaGuard - AppEEARS ID / CELL MAPPING DIAGNOSTIC")
print("=" * 80)

ndvi = pd.read_csv(NDVI_PATH)
pa = pd.read_csv(PA_PATH)

print("\n=== APPEEARS ID STRUCTURE ===")

print("Unique AppEEARS IDs:", ndvi["ID"].nunique())
print("Total AppEEARS rows:", len(ndvi))

print("\nFirst 30 IDs:")
print(
    ndvi[
        ["ID", "Latitude", "Longitude", "Date"]
    ]
    .drop_duplicates("ID")
    .head(30)
    .to_string(index=False)
)

print("\n=== ID COUNTS ===")

print(
    ndvi["ID"]
    .value_counts()
    .describe()
)

print("\n=== PSEUDO-ABSENCE CELLS ===")

print(
    "Unique PA cells:",
    pa["grid_cell_id"].nunique()
)

print(
    pa[
        ["grid_cell_id", "decimalLatitude", "decimalLongitude"]
    ]
    .drop_duplicates("grid_cell_id")
    .head(30)
    .to_string(index=False)
)

print("\n=== APPEEARS COORDINATE RANGE ===")

print(
    "Latitude:",
    ndvi["Latitude"].min(),
    "to",
    ndvi["Latitude"].max()
)

print(
    "Longitude:",
    ndvi["Longitude"].min(),
    "to",
    ndvi["Longitude"].max()
)

print("\n=== PA COORDINATE RANGE ===")

print(
    "Latitude:",
    pa["decimalLatitude"].min(),
    "to",
    pa["decimalLatitude"].max()
)

print(
    "Longitude:",
    pa["decimalLongitude"].min(),
    "to",
    pa["decimalLongitude"].max()
)

print("\n=== UNIQUE APPEEARS POINTS ===")

points = (
    ndvi[
        ["ID", "Latitude", "Longitude"]
    ]
    .drop_duplicates()
    .sort_values("ID")
)

print(
    "Unique ID/coordinate combinations:",
    len(points)
)

print(points.to_string(index=False))

print("\n=== CHECKING WHETHER APPEEARS IDS LOOK LIKE GRID IDS ===")

ids = ndvi["ID"].astype(str).drop_duplicates().tolist()

for value in ids[:50]:
    print(repr(value))

print("\n=== DIAGNOSTIC COMPLETE ===")
print("NO FILES WERE MODIFIED.")
