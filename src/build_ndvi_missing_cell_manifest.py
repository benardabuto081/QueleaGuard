from pathlib import Path
import pandas as pd

print("=" * 80)
print("QueleaGuard - NDVI MISSING CELL EXTRACTION MANIFEST")
print("=" * 80)

ROOT = Path(__file__).resolve().parents[1]

PA_FILE = (
    ROOT
    / "data"
    / "processed"
    / "pseudo_absences_final.csv"
)

NDVI_FILE = (
    ROOT
    / "data"
    / "processed"
    / "ndvi_features_pseudo_absence.csv"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "processed"
    / "ndvi_missing_cells_manifest.csv"
)

# ---------------------------------------------------------------------
# LOAD PA DATA
# ---------------------------------------------------------------------

print("\n=== LOADING PA DATA ===")

pa = pd.read_csv(PA_FILE)

print(f"PA records: {len(pa):,}")

# ---------------------------------------------------------------------
# LOAD CURRENT NDVI OUTPUT
# ---------------------------------------------------------------------

print("\n=== LOADING CURRENT NDVI OUTPUT ===")

ndvi = pd.read_csv(NDVI_FILE)

print(f"NDVI aligned records: {len(ndvi):,}")

# ---------------------------------------------------------------------
# CELL SETS
# ---------------------------------------------------------------------

pa_cells = set(
    pa["grid_cell_id"]
    .astype(str)
    .str.strip()
)

ndvi_cells = set(
    ndvi["grid_cell_id"]
    .astype(str)
    .str.strip()
)

missing_cells = sorted(
    pa_cells - ndvi_cells
)

covered_cells = sorted(
    pa_cells & ndvi_cells
)

print("\n=== COVERAGE ===")

print(f"Unique PA cells:       {len(pa_cells):,}")
print(f"Covered NDVI cells:    {len(covered_cells):,}")
print(f"Missing NDVI cells:    {len(missing_cells):,}")

# ---------------------------------------------------------------------
# BUILD MANIFEST
# ---------------------------------------------------------------------

print("\n=== BUILDING MISSING CELL MANIFEST ===")

manifest = (
    pa[
        pa["grid_cell_id"]
        .astype(str)
        .str.strip()
        .isin(missing_cells)
    ]
    .copy()
)

# Normalize IDs
manifest["grid_cell_id"] = (
    manifest["grid_cell_id"]
    .astype(str)
    .str.strip()
)

# Normalize dates
manifest["_event_datetime"] = pd.to_datetime(
    manifest["eventDate"],
    format="mixed",
    errors="coerce",
    utc=True,
)

manifest["_event_date"] = (
    manifest["_event_datetime"]
    .dt.normalize()
    .dt.tz_localize(None)
)

# ---------------------------------------------------------------------
# CELL-LEVEL SUMMARY
# ---------------------------------------------------------------------

cell_summary = (
    manifest
    .groupby("grid_cell_id")
    .agg(
        pa_record_count=("grid_cell_id", "size"),
        first_event_date=("_event_date", "min"),
        last_event_date=("_event_date", "max"),
        latitude=("decimalLatitude", "first"),
        longitude=("decimalLongitude", "first"),
    )
    .reset_index()
)

# ---------------------------------------------------------------------
# PRINT SUMMARY
# ---------------------------------------------------------------------

print("\n=== MISSING CELL SUMMARY ===")

print(
    cell_summary
    .sort_values("grid_cell_id")
    .to_string(index=False)
)

# ---------------------------------------------------------------------
# RECORD COVERAGE BY CELL
# ---------------------------------------------------------------------

print("\n=== RECORDS REQUIRING NDVI ===")

print(
    f"Records requiring additional NDVI: "
    f"{len(manifest):,}"
)

# ---------------------------------------------------------------------
# SAVE
# ---------------------------------------------------------------------

cell_summary.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n=== SAVING ===")

print(
    f"Manifest written to:\n{OUTPUT_FILE}"
)

print(
    f"Missing cells written: {len(cell_summary):,}"
)

# ---------------------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------------------

assert len(cell_summary) == len(missing_cells)

assert (
    set(cell_summary["grid_cell_id"])
    == set(missing_cells)
)

print("\n=== VALIDATION ===")

print("[PASS] Every uncovered PA cell is represented.")
print("[PASS] No already-covered cell included.")
print("[PASS] Manifest contains cell coordinates.")
print("[PASS] Manifest contains temporal range.")
print("[PASS] Manifest contains PA record counts.")

print("\n" + "=" * 80)
print("MISSING CELL MANIFEST COMPLETE")
print("=" * 80)

print(
    "\nNEXT STEP:"
)

print(
    "Use this manifest to construct the second AppEEARS "
    "NDVI extraction task."
)

