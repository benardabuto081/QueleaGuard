from pathlib import Path
import pandas as pd

ROOT = Path(".")

PA = ROOT / "data/processed/pseudo_absences_final.csv"
CHIRPS = ROOT / "data/processed/rainfall_features_pseudo_absence.csv"

TARGETS = ["3030315394", "3030714769"]

print("=" * 80)
print("QUELEAGUARD — TARGETED CHIRPS MISSING-RECORD FORENSIC AUDIT")
print("=" * 80)

pa = pd.read_csv(PA)
chirps = pd.read_csv(CHIRPS)

pa["key"] = pa["key"].astype(str)
chirps["record_key"] = chirps["record_key"].astype(str)

print("\nCURRENT PA DATASET")
print("-" * 80)
print(f"Rows: {len(pa)}")
print(f"Unique keys: {pa['key'].nunique()}")

print("\nTARGET RECORDS")
print("-" * 80)

targets = pa[pa["key"].isin(TARGETS)].copy()

if targets.empty:
    print("ERROR: Neither target key exists in current PA dataset.")
else:
    print(targets.to_string(index=False))

print("\nCHIRPS MATCH CHECK")
print("-" * 80)

for key in TARGETS:
    pa_row = pa[pa["key"] == key]

    if pa_row.empty:
        print(f"\n{key}: NOT FOUND IN CURRENT PA DATASET")
        continue

    chirps_row = chirps[chirps["record_key"] == key]

    print(f"\nKEY: {key}")

    print("PA RECORD:")
    print(pa_row.to_string(index=False))

    if chirps_row.empty:
        print("CHIRPS: MISSING")
    else:
        print("CHIRPS: FOUND")
        print(chirps_row.to_string(index=False))

print("\n" + "=" * 80)
print("GRID-CELL / DATE SUMMARY")
print("=" * 80)

for key in TARGETS:
    row = pa[pa["key"] == key]

    if row.empty:
        continue

    row = row.iloc[0]

    print(
        f"\n{key}"
        f"\n  grid_cell_id: {row.get('grid_cell_id')}"
        f"\n  observation_date: {row.get('observation_date')}"
        f"\n  latitude: {row.get('latitude')}"
        f"\n  longitude: {row.get('longitude')}"
    )

print("\n" + "=" * 80)
print("EXISTING CHIRPS DATASET DATE/CELL COVERAGE")
print("=" * 80)

print("\nCHIRPS columns:")
print(list(chirps.columns))

print("\nCHIRPS date range:")
if "observation_date" in chirps.columns:
    dates = pd.to_datetime(chirps["observation_date"], errors="coerce")
    print(f"  min: {dates.min()}")
    print(f"  max: {dates.max()}")
    print(f"  invalid dates: {dates.isna().sum()}")

print("\nCHIRPS unique grid cells:")
if "grid_cell_id" in chirps.columns:
    print(f"  {chirps['grid_cell_id'].nunique()}")

print("\nCHIRPS rows by grid cell:")
if "grid_cell_id" in chirps.columns:
    print(chirps["grid_cell_id"].value_counts().sort_index().to_string())

print("\n" + "=" * 80)
print("PA GRID-CELL COVERAGE VS CHIRPS")
print("=" * 80)

if "grid_cell_id" in chirps.columns and "grid_cell_id" in pa.columns:

    pa_cells = set(pa["grid_cell_id"].astype(str))
    chirps_cells = set(chirps["grid_cell_id"].astype(str))

    print(f"PA unique cells: {len(pa_cells)}")
    print(f"CHIRPS unique cells: {len(chirps_cells)}")

    missing_cells = pa_cells - chirps_cells
    extra_cells = chirps_cells - pa_cells

    print(f"PA cells absent from CHIRPS: {len(missing_cells)}")

    if missing_cells:
        print(sorted(missing_cells))

    print(f"CHIRPS cells absent from PA: {len(extra_cells)}")

    if extra_cells:
        print(sorted(extra_cells))

print("\n" + "=" * 80)
print("FORENSIC AUDIT COMPLETE — NO FILES MODIFIED")
print("=" * 80)
