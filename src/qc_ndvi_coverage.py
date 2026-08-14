from pathlib import Path
import pandas as pd
import numpy as np

print("=" * 80)
print("QueleaGuard - NDVI COVERAGE & FINAL QC")
print("=" * 80)

ROOT = Path(__file__).resolve().parents[1]

PA_FILE = ROOT / "data" / "processed" / "pseudo_absences_final.csv"
NDVI_FILE = ROOT / "data" / "processed" / "ndvi_features_pseudo_absence.csv"

# ---------------------------------------------------------------------
# LOAD FILES
# ---------------------------------------------------------------------

print("\n=== LOADING DATASETS ===")

pa = pd.read_csv(PA_FILE)
ndvi = pd.read_csv(NDVI_FILE)

print(f"Pseudo-absence records: {len(pa):,}")
print(f"NDVI aligned records:   {len(ndvi):,}")

# ---------------------------------------------------------------------
# REQUIRED COLUMNS
# ---------------------------------------------------------------------

required_pa = {
    "grid_cell_id",
    "eventDate",
}

required_ndvi = {
    "grid_cell_id",
    "eventDate",
    "event_date",
    "ndvi_aligned_date",
    "ndvi",
    "ndvi_raw",
    "ndvi_temporal_distance_days",
    "ndvi_temporal_alignment",
}

missing_pa = required_pa - set(pa.columns)
missing_ndvi = required_ndvi - set(ndvi.columns)

if missing_pa:
    raise RuntimeError(
        f"Missing PA columns: {sorted(missing_pa)}"
    )

if missing_ndvi:
    raise RuntimeError(
        f"Missing NDVI columns: {sorted(missing_ndvi)}"
    )

# ---------------------------------------------------------------------
# NORMALIZE CELL IDS
# ---------------------------------------------------------------------

pa["grid_cell_id"] = pa["grid_cell_id"].astype(str).str.strip()
ndvi["grid_cell_id"] = ndvi["grid_cell_id"].astype(str).str.strip()

# ---------------------------------------------------------------------
# NORMALIZE DATES
# ---------------------------------------------------------------------

pa["_event_date"] = pd.to_datetime(
    pa["eventDate"],
    format="mixed",
    errors="coerce",
    utc=True,
).dt.normalize().dt.tz_localize(None)

ndvi["_event_date"] = pd.to_datetime(
    ndvi["event_date"],
    format="mixed",
    errors="coerce",
)

print("\n=== DATE QC ===")

print(
    f"PA dates failed:   {pa['_event_date'].isna().sum():,}"
)

print(
    f"NDVI dates failed: {ndvi['_event_date'].isna().sum():,}"
)

# ---------------------------------------------------------------------
# CELL COVERAGE
# ---------------------------------------------------------------------

pa_cells = set(pa["grid_cell_id"].unique())
ndvi_cells = set(ndvi["grid_cell_id"].unique())

covered_cells = pa_cells & ndvi_cells
missing_cells = pa_cells - ndvi_cells

print("\n=== CELL COVERAGE ===")

print(f"Unique PA cells:       {len(pa_cells):,}")
print(f"Unique NDVI cells:     {len(ndvi_cells):,}")
print(f"Covered PA cells:      {len(covered_cells):,}")
print(f"Uncovered PA cells:    {len(missing_cells):,}")

if missing_cells:
    print("\nCells missing NDVI:")
    for cell in sorted(missing_cells):
        print(f"  {cell}")

# ---------------------------------------------------------------------
# RECORD COVERAGE
# ---------------------------------------------------------------------

ndvi_keys = set(
    zip(
        ndvi["grid_cell_id"],
        ndvi["_event_date"],
    )
)

pa["_ndvi_key"] = list(
    zip(
        pa["grid_cell_id"],
        pa["_event_date"],
    )
)

pa["has_ndvi"] = pa["_ndvi_key"].isin(ndvi_keys)

covered_records = int(pa["has_ndvi"].sum())
missing_records = len(pa) - covered_records

print("\n=== RECORD COVERAGE ===")

print(f"Total PA records:       {len(pa):,}")
print(f"Records with NDVI:      {covered_records:,}")
print(f"Records without NDVI:   {missing_records:,}")

coverage_pct = (
    covered_records / len(pa) * 100
    if len(pa) > 0
    else 0
)

print(f"Record coverage:        {coverage_pct:.2f}%")

# ---------------------------------------------------------------------
# NDVI VALUE QC
# ---------------------------------------------------------------------

ndvi_values = pd.to_numeric(
    ndvi["ndvi"],
    errors="coerce",
)

print("\n=== NDVI VALUE QC ===")

print(f"Valid NDVI values:      {ndvi_values.notna().sum():,}")
print(f"Missing NDVI values:    {ndvi_values.isna().sum():,}")

print("\nNDVI statistics:")
print(ndvi_values.describe())

invalid_low = (ndvi_values < -1).sum()
invalid_high = (ndvi_values > 1).sum()

print("\nPhysical range check:")
print(f"NDVI < -1:              {invalid_low:,}")
print(f"NDVI > 1:               {invalid_high:,}")

# ---------------------------------------------------------------------
# RAW FILL VALUE QC
# ---------------------------------------------------------------------

raw_values = pd.to_numeric(
    ndvi["ndvi_raw"],
    errors="coerce",
)

fill_values = (raw_values == -3000).sum()

print("\n=== FILL VALUE QC ===")

print(f"Raw -3000 fill values:  {fill_values:,}")

# ---------------------------------------------------------------------
# TEMPORAL QC
# ---------------------------------------------------------------------

distance = pd.to_numeric(
    ndvi["ndvi_temporal_distance_days"],
    errors="coerce",
)

print("\n=== TEMPORAL QC ===")

print(f"Maximum temporal gap:   {distance.max():.0f} days")
print(f"Median temporal gap:    {distance.median():.1f} days")
print(f"Mean temporal gap:      {distance.mean():.2f} days")

print("\nTemporal distance distribution:")
print(
    distance
    .value_counts()
    .sort_index()
    .to_string()
)

# ---------------------------------------------------------------------
# ALIGNMENT DIRECTION
# ---------------------------------------------------------------------

print("\n=== ALIGNMENT DIRECTION ===")

print(
    ndvi["ndvi_temporal_alignment"]
    .value_counts(dropna=False)
    .to_string()
)

# ---------------------------------------------------------------------
# DUPLICATE CHECK
# ---------------------------------------------------------------------

duplicates = ndvi.duplicated(
    subset=[
        "grid_cell_id",
        "_event_date",
    ]
).sum()

print("\n=== DUPLICATE CHECK ===")

print(
    f"Duplicate cell/event-date records: {duplicates:,}"
)

# ---------------------------------------------------------------------
# FINAL VERDICT
# ---------------------------------------------------------------------

print("\n" + "=" * 80)
print("FINAL NDVI QC VERDICT")
print("=" * 80)

checks = {
    "All PA dates parsed": pa["_event_date"].notna().all(),
    "All NDVI dates parsed": ndvi["_event_date"].notna().all(),
    "No invalid NDVI < -1": invalid_low == 0,
    "No invalid NDVI > 1": invalid_high == 0,
    "No duplicate cell/date records": duplicates == 0,
    "Maximum temporal gap <= 8 days": distance.max() <= 8,
    "All aligned NDVI values present": ndvi_values.notna().all(),
}

for name, passed in checks.items():
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}")

print("\n=== COVERAGE SUMMARY ===")

print(
    f"PA records covered by current NDVI bundle: "
    f"{covered_records}/{len(pa)} ({coverage_pct:.2f}%)"
)

if missing_records > 0:
    print(
        "\nWARNING:"
        "\nThe current AppEEARS task does not cover all PA records."
        "\nDo NOT proceed to final modeling yet."
        "\nAdditional NDVI extraction is required for the uncovered cells."
    )
else:
    print(
        "\nSUCCESS:"
        "\nAll pseudo-absence records have NDVI coverage."
    )

print("\n" + "=" * 80)
print("NDVI COVERAGE & FINAL QC COMPLETE")
print("=" * 80)
