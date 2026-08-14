from pathlib import Path
import pandas as pd
import geopandas as gpd

ROOT = Path(".")
GAP_PATH = ROOT / "data/processed/true_ndvi_missing_cells.csv"
GRID_PATH = ROOT / "data/processed/analysis_grid.geojson"
OUT_PATH = ROOT / "data/processed/ndvi_second_task_spec.csv"

print("=" * 80)
print("QUELEAGUARD - BUILD FINAL NDVI GAP TASK SPECIFICATION")
print("=" * 80)

# ------------------------------------------------------------
# 1. LOAD TRUE NDVI GAP
# ------------------------------------------------------------
if not GAP_PATH.exists():
    raise FileNotFoundError(f"Missing gap manifest: {GAP_PATH}")

gap = pd.read_csv(GAP_PATH)

if "grid_cell_id" not in gap.columns:
    raise ValueError("Gap manifest must contain grid_cell_id.")

missing_cells = sorted(
    gap["grid_cell_id"]
    .dropna()
    .astype(str)
    .unique()
)

print(f"\nTrue missing NDVI cells: {len(missing_cells)}")

# ------------------------------------------------------------
# 2. LOAD GRID
# ------------------------------------------------------------
print("\n=== LOADING GRID ===")

grid = gpd.read_file(GRID_PATH)

required = {"grid_cell_id", "geometry"}
missing_columns = required - set(grid.columns)

if missing_columns:
    raise ValueError(
        f"Grid missing required columns: {sorted(missing_columns)}"
    )

print(f"Grid rows: {len(grid)}")
print(f"Grid CRS:  {grid.crs}")

# ------------------------------------------------------------
# 3. SELECT THE 36 TRUE GAP CELLS
# ------------------------------------------------------------
grid["grid_cell_id"] = grid["grid_cell_id"].astype(str)

selected = grid[
    grid["grid_cell_id"].isin(missing_cells)
].copy()

if len(selected) != len(missing_cells):
    found = set(selected["grid_cell_id"])
    unresolved = sorted(set(missing_cells) - found)

    raise ValueError(
        f"Could not resolve {len(unresolved)} gap cells:\n"
        + "\n".join(unresolved)
    )

print(f"Resolved gap cells: {len(selected)}")

# ------------------------------------------------------------
# 4. CONVERT TO WGS84
# ------------------------------------------------------------
print("\n=== DERIVING WGS84 CENTROIDS ===")

if selected.crs is None:
    raise ValueError("Grid CRS is undefined.")

selected_wgs84 = selected.to_crs("EPSG:4326")

# Project first, then centroid, avoiding geographic-centroid issues.
selected_projected = selected.to_crs(
    selected.estimate_utm_crs()
)

centroids_projected = selected_projected.geometry.centroid

centroids_wgs84 = gpd.GeoSeries(
    centroids_projected,
    crs=selected_projected.crs
).to_crs("EPSG:4326")

task = pd.DataFrame({
    "grid_cell_id": selected_projected["grid_cell_id"].values,
    "latitude": centroids_wgs84.y.values,
    "longitude": centroids_wgs84.x.values,
})

task["latitude"] = task["latitude"].round(6)
task["longitude"] = task["longitude"].round(6)

task = task.sort_values("grid_cell_id").reset_index(drop=True)

# ------------------------------------------------------------
# 5. VALIDATION
# ------------------------------------------------------------
print("\n=== VALIDATION ===")

if len(task) != 36:
    raise ValueError(
        f"Expected exactly 36 cells, found {len(task)}."
    )

if task["grid_cell_id"].duplicated().any():
    raise ValueError("Duplicate grid_cell_id detected.")

if task[["latitude", "longitude"]].isna().any().any():
    raise ValueError("Missing coordinates detected.")

if not task["latitude"].between(-90, 90).all():
    raise ValueError("Invalid latitude detected.")

if not task["longitude"].between(-180, 180).all():
    raise ValueError("Invalid longitude detected.")

print("[PASS] Exactly 36 cells.")
print("[PASS] All grid cells resolved.")
print("[PASS] All coordinates valid.")
print("[PASS] No duplicate cells.")
print("[PASS] Coordinates transformed to WGS84.")

# ------------------------------------------------------------
# 6. PRINT FINAL COORDINATES
# ------------------------------------------------------------
print("\n" + "=" * 80)
print("FINAL 36-CELL APPEEARS TASK COORDINATES")
print("=" * 80)

print(
    task.to_string(index=False)
)

# ------------------------------------------------------------
# 7. SAVE
# ------------------------------------------------------------
task.to_csv(OUT_PATH, index=False)

print("\n" + "=" * 80)
print("FINAL NDVI GAP TASK SPECIFICATION COMPLETE")
print("=" * 80)

print(f"Saved: {OUT_PATH}")
print(f"Cells: {len(task)}")
print("\nDO NOT submit yet.")
print("Review the generated coordinates first.")
