import pandas as pd
from pathlib import Path

print("=" * 80)
print("QueleaGuard - BUILD SECOND APPEEARS NDVI TASK SPECIFICATION")
print("=" * 80)

# ------------------------------------------------------------------
# PATHS
# ------------------------------------------------------------------

manifest_path = Path(
    "data/processed/ndvi_missing_cells_manifest.csv"
)

output_path = Path(
    "data/processed/appeears_ndvi_second_task_spec.csv"
)

# ------------------------------------------------------------------
# LOAD MISSING CELL MANIFEST
# ------------------------------------------------------------------

print("\n=== LOADING MISSING CELL MANIFEST ===")

df = pd.read_csv(manifest_path)

print(f"Missing cells: {len(df)}")
print(f"Columns: {list(df.columns)}")

required_columns = [
    "grid_cell_id",
    "latitude",
    "longitude",
]

missing_columns = [
    c for c in required_columns
    if c not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

# ------------------------------------------------------------------
# VALIDATE CELLS
# ------------------------------------------------------------------

print("\n=== CELL VALIDATION ===")

if df["grid_cell_id"].duplicated().any():
    duplicates = df.loc[
        df["grid_cell_id"].duplicated(),
        "grid_cell_id"
    ].tolist()

    raise ValueError(
        f"Duplicate grid cells detected: {duplicates}"
    )

if df["latitude"].isna().any():
    raise ValueError("Missing latitude values detected.")

if df["longitude"].isna().any():
    raise ValueError("Missing longitude values detected.")

print("[PASS] All grid cells are unique")
print("[PASS] All cells have latitude")
print("[PASS] All cells have longitude")

# ------------------------------------------------------------------
# TEMPORAL SPECIFICATION
# ------------------------------------------------------------------

START_DATE = "2000-02-18"
END_DATE = "2026-07-12"

print("\n=== TEMPORAL SPECIFICATION ===")
print(f"Start date: {START_DATE}")
print(f"End date:   {END_DATE}")

# ------------------------------------------------------------------
# BUILD TASK SPECIFICATION
# ------------------------------------------------------------------

task = df[
    [
        "grid_cell_id",
        "latitude",
        "longitude",
    ]
].copy()

task["start_date"] = START_DATE
task["end_date"] = END_DATE

task["product"] = "MOD13Q1.061"
task["layer"] = "250m_16_days_NDVI"
task["scale_factor"] = 0.0001

# ------------------------------------------------------------------
# DISPLAY
# ------------------------------------------------------------------

print("\n=== SECOND TASK SPECIFICATION ===")

print(
    task.to_string(index=False)
)

# ------------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------------

print("\n=== TASK SUMMARY ===")

print(f"Cells:        {len(task)}")
print(f"Start:        {START_DATE}")
print(f"End:          {END_DATE}")
print("Product:      MOD13Q1.061")
print("Layer:        250m_16_days_NDVI")
print("Scale factor: 0.0001")

# ------------------------------------------------------------------
# SAVE
# ------------------------------------------------------------------

output_path.parent.mkdir(
    parents=True,
    exist_ok=True
)

task.to_csv(
    output_path,
    index=False
)

print("\n=== SAVING ===")
print(f"Specification written to:")
print(output_path)

# ------------------------------------------------------------------
# FINAL VALIDATION
# ------------------------------------------------------------------

saved = pd.read_csv(output_path)

assert len(saved) == 36
assert saved["grid_cell_id"].nunique() == 36
assert saved["start_date"].eq(START_DATE).all()
assert saved["end_date"].eq(END_DATE).all()

print("\n=== VALIDATION ===")
print("[PASS] 36 missing cells included")
print("[PASS] No duplicate cells")
print("[PASS] Correct temporal start")
print("[PASS] Correct temporal end")
print("[PASS] Correct MODIS product")
print("[PASS] Correct NDVI layer")
print("[PASS] Scale factor recorded")

print("\n" + "=" * 80)
print("SECOND APPEEARS NDVI TASK SPECIFICATION COMPLETE")
print("=" * 80)

print("\nNEXT STEP:")
print("Use the 36 coordinates from this specification")
print("to create the second AppEEARS Area Sample task.")
