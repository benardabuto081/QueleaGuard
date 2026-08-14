from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

print("=" * 80)
print("QUELEAGUARD - ENVIRONMENTAL DATA INVENTORY")
print("=" * 80)

DATA_DIRS = [
    ROOT / "data" / "processed",
    ROOT / "data" / "external",
]

EXTENSIONS = {".csv", ".parquet", ".geojson", ".json"}

files = []

for directory in DATA_DIRS:
    if not directory.exists():
        continue

    for path in sorted(directory.rglob("*")):
        if path.is_file() and path.suffix.lower() in EXTENSIONS:
            files.append(path)

print()
print(f"Project root: {ROOT}")
print(f"Candidate data files: {len(files)}")

print()
print("=" * 80)
print("FILES")
print("=" * 80)

for i, path in enumerate(files, 1):
    size_mb = path.stat().st_size / (1024 * 1024)
    print(f"{i:03d}. {path.relative_to(ROOT)} ({size_mb:.2f} MB)")

print()
print("=" * 80)
print("TABULAR DATASET INSPECTION")
print("=" * 80)

for path in files:

    if path.suffix.lower() not in {".csv", ".parquet"}:
        continue

    print()
    print("-" * 80)
    print(path.relative_to(ROOT))
    print("-" * 80)

    try:

        if path.suffix.lower() == ".csv":
            df = pd.read_csv(path, nrows=5)
        else:
            df = pd.read_parquet(path).head(5)

        print(f"Columns ({len(df.columns)}):")
        print(list(df.columns))

        print()
        print("Sample:")
        print(df.to_string(index=False))

    except Exception as exc:
        print(f"[ERROR] Could not inspect file: {exc}")

print()
print("=" * 80)
print("INVENTORY COMPLETE")
print("=" * 80)
