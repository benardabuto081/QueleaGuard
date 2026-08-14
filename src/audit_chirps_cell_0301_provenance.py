from pathlib import Path
import pandas as pd
import re

ROOT = Path(".")

TARGET_KEYS = ["3030315394", "3030714769"]
TARGET_CELL = "cell_0301"

print("=" * 100)
print("QUELEAGUARD — CHIRPS CELL_0301 PROVENANCE FORENSIC AUDIT")
print("=" * 100)

# ============================================================
# 1. CURRENT PA RECORDS — CORRECT COLUMN NAMES
# ============================================================

print("\n" + "=" * 100)
print("PART 1 — CURRENT CORRECTED PA RECORDS")
print("=" * 100)

pa_path = ROOT / "data/processed/pseudo_absences_final.csv"
pa = pd.read_csv(pa_path)

pa["key"] = pa["key"].astype(str)

targets = pa[pa["key"].isin(TARGET_KEYS)].copy()

print(f"PA rows: {len(pa)}")
print(f"PA unique keys: {pa['key'].nunique()}")

if targets.empty:
    print("ERROR: Target records not found.")
else:
    cols = [
        "key",
        "scientificName",
        "decimalLatitude",
        "decimalLongitude",
        "eventDate",
        "year",
        "grid_cell_id",
        "within_scheme_boundary",
        "record_type",
        "presence",
    ]

    cols = [c for c in cols if c in targets.columns]

    print("\nTarget records:")
    print(targets[cols].to_string(index=False))

# ============================================================
# 2. ALL PA RECORDS IN CELL_0301
# ============================================================

print("\n" + "=" * 100)
print("PART 2 — ALL CURRENT PA RECORDS IN CELL_0301")
print("=" * 100)

cell_rows = pa[pa["grid_cell_id"].astype(str) == TARGET_CELL].copy()

print(f"Current PA records in {TARGET_CELL}: {len(cell_rows)}")

if not cell_rows.empty:
    cols = [
        "key",
        "decimalLatitude",
        "decimalLongitude",
        "eventDate",
        "year",
        "grid_cell_id",
        "within_scheme_boundary",
        "record_type",
        "presence",
    ]

    cols = [c for c in cols if c in cell_rows.columns]

    print(cell_rows[cols].to_string(index=False))

# ============================================================
# 3. GRID MAPPING / GRID FILE DISCOVERY
# ============================================================

print("\n" + "=" * 100)
print("PART 3 — GRID / CELL_0301 MAPPING")
print("=" * 100)

grid_candidates = []

for directory in [
    ROOT / "data/processed",
    ROOT / "data/external",
    ROOT / "data/raw",
]:
    if not directory.exists():
        continue

    for p in directory.rglob("*"):
        if p.is_file():
            name = p.name.lower()

            if any(term in name for term in [
                "grid",
                "mapping",
                "cell",
                "ahero"
            ]):
                grid_candidates.append(p)

print(f"Potential grid/mapping files found: {len(grid_candidates)}")

for p in sorted(set(grid_candidates)):
    print(f"\n--- {p} ---")

    if p.suffix.lower() == ".csv":
        try:
            df = pd.read_csv(p)

            matching = pd.DataFrame()

            for col in df.columns:
                if df[col].astype(str).eq(TARGET_CELL).any():
                    matching = df[
                        df[col].astype(str) == TARGET_CELL
                    ]

                    print(
                        f"Found {TARGET_CELL} in column '{col}'"
                    )
                    print(matching.to_string(index=False))
                    break

        except Exception as e:
            print(f"Could not parse CSV: {type(e).__name__}: {e}")

# ============================================================
# 4. CHIRPS FILE INVENTORY
# ============================================================

print("\n" + "=" * 100)
print("PART 4 — CHIRPS FILE INVENTORY")
print("=" * 100)

chirps_files = []

for directory in [
    ROOT / "data/raw",
    ROOT / "data/external",
    ROOT / "data/processed",
]:
    if not directory.exists():
        continue

    for p in directory.rglob("*"):
        if p.is_file() and "chirps" in p.name.lower():
            chirps_files.append(p)

for p in sorted(set(chirps_files)):

    print(f"\n{p}")

    try:
        size_mb = p.stat().st_size / (1024 * 1024)
        print(f"  size: {size_mb:.2f} MB")
    except:
        pass

    if p.suffix.lower() == ".csv":
        try:
            df = pd.read_csv(p)

            print(f"  rows: {len(df):,}")
            print(f"  columns: {len(df.columns)}")
            print(f"  columns: {list(df.columns)}")

        except Exception as e:
            print(f"  parser error: {type(e).__name__}: {e}")

# ============================================================
# 5. CURRENT CHIRPS OUTPUT
# ============================================================

print("\n" + "=" * 100)
print("PART 5 — CURRENT CHIRPS OUTPUT")
print("=" * 100)

chirps_path = ROOT / "data/processed/rainfall_features_pseudo_absence.csv"

chirps = pd.read_csv(chirps_path)

chirps["record_key"] = chirps["record_key"].astype(str)
chirps["grid_cell_id"] = chirps["grid_cell_id"].astype(str)

print(f"Rows: {len(chirps)}")
print(f"Unique record keys: {chirps['record_key'].nunique()}")
print(f"Unique grid cells: {chirps['grid_cell_id'].nunique()}")

print("\nAny cell_0301 rows?")
cell_chirps = chirps[
    chirps["grid_cell_id"] == TARGET_CELL
]

if cell_chirps.empty:
    print("NO — cell_0301 is completely absent.")
else:
    print(cell_chirps.to_string(index=False))

# ============================================================
# 6. SEARCH ALL PYTHON SOURCE FOR CHIRPS LOGIC
# ============================================================

print("\n" + "=" * 100)
print("PART 6 — CHIRPS EXTRACTION SOURCE CODE DISCOVERY")
print("=" * 100)

py_files = list((ROOT / "src").rglob("*.py"))

for p in sorted(py_files):

    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except:
        continue

    lower = text.lower()

    if "chirps" in lower or "rainfall_features" in lower:

        print(f"\n{'-' * 100}")
        print(f"SOURCE: {p}")
        print(f"{'-' * 100}")

        lines = text.splitlines()

        for i, line in enumerate(lines, start=1):

            if any(term in line.lower() for term in [
                "chirps",
                "rainfall_features",
                "pseudo_absence",
                "grid_cell_id",
                "eventdate",
                "observation_date",
                "record_key",
                "skip",
                "continue",
                "filter",
            ]):

                start = max(1, i - 2)
                end = min(len(lines), i + 2)

                print(
                    f"\n[{start}-{end}]"
                )

                for j in range(start, end + 1):
                    print(
                        f"{j:4}: {lines[j-1]}"
                    )

# ============================================================
# 7. SEARCH REPOSITORY FOR CELL_0301
# ============================================================

print("\n" + "=" * 100)
print("PART 7 — REPOSITORY-WIDE CELL_0301 SEARCH")
print("=" * 100)

matches = []

for p in ROOT.rglob("*"):

    if not p.is_file():
        continue

    # Skip obvious large/binary/environment files
    if any(part in {
        ".git",
        ".venv",
        "venv",
        "__pycache__"
    } for part in p.parts):
        continue

    if p.suffix.lower() not in {
        ".py",
        ".csv",
        ".txt",
        ".md",
        ".json",
        ".yaml",
        ".yml"
    }:
        continue

    try:
        text = p.read_text(
            encoding="utf-8",
            errors="ignore"
        )
    except:
        continue

    if TARGET_CELL in text:
        occurrences = text.count(TARGET_CELL)

        matches.append((p, occurrences))

for p, occurrences in sorted(matches):

    print(
        f"{p} -> {occurrences} occurrence(s)"
    )

# ============================================================
# 8. CURRENT PA CELL COVERAGE VS CHIRPS
# ============================================================

print("\n" + "=" * 100)
print("PART 8 — CELL COVERAGE RECONCILIATION")
print("=" * 100)

pa_cells = set(
    pa["grid_cell_id"]
    .dropna()
    .astype(str)
)

chirps_cells = set(
    chirps["grid_cell_id"]
    .dropna()
    .astype(str)
)

print(f"PA cells: {len(pa_cells)}")
print(f"CHIRPS cells: {len(chirps_cells)}")

missing_cells = pa_cells - chirps_cells

print(f"PA cells missing from CHIRPS: {len(missing_cells)}")
print(sorted(missing_cells))

# ============================================================
# 9. TEMPORAL DETAILS FOR THE TWO TARGETS
# ============================================================

print("\n" + "=" * 100)
print("PART 9 — TARGET TEMPORAL DETAILS")
print("=" * 100)

for key in TARGET_KEYS:

    row = pa[pa["key"] == key]

    if row.empty:
        continue

    row = row.iloc[0]

    print(
        f"\nKEY: {key}"
    )

    print(
        f"  eventDate: {row.get('eventDate')}"
    )

    print(
        f"  year: {row.get('year')}"
    )

    print(
        f"  grid_cell_id: {row.get('grid_cell_id')}"
    )

    print(
        f"  latitude: {row.get('decimalLatitude')}"
    )

    print(
        f"  longitude: {row.get('decimalLongitude')}"
    )

print("\n" + "=" * 100)
print("FORENSIC AUDIT COMPLETE")
print("READ-ONLY — NO FILES MODIFIED")
print("=" * 100)

