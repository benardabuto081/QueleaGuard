from pathlib import Path
import pandas as pd

print("=" * 80)
print("QueleaGuard - APPEEARS NDVI TEMPORAL RANGE INSPECTION")
print("=" * 80)

ROOT = Path(__file__).resolve().parents[1]

NDVI_DIR = (
    ROOT
    / "data"
    / "external"
    / "appeears_ndvi_pa_v2_gap_45cells"
)

csv_files = sorted(NDVI_DIR.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError(
        f"No AppEEARS CSV found in:\n{NDVI_DIR}"
    )

ndvi_file = csv_files[0]

print("\n=== FILE ===")
print(ndvi_file)

ndvi = pd.read_csv(ndvi_file)

print(f"\nRows: {len(ndvi):,}")

# ---------------------------------------------------------------------
# DATE PARSING
# ---------------------------------------------------------------------

print("\n=== DATE RANGE ===")

dates = pd.to_datetime(
    ndvi["Date"],
    format="mixed",
    errors="coerce",
    utc=True,
)

failed = dates.isna()

print(f"Dates parsed:  {(~failed).sum():,}")
print(f"Dates failed:  {failed.sum():,}")

if failed.any():
    raise RuntimeError("NDVI dates failed parsing.")

dates = dates.dt.normalize()

unique_dates = (
    dates
    .drop_duplicates()
    .sort_values()
)

print(f"\nUnique NDVI dates: {len(unique_dates):,}")
print(f"Earliest NDVI date: {unique_dates.min()}")
print(f"Latest NDVI date:   {unique_dates.max()}")

# ---------------------------------------------------------------------
# YEAR DISTRIBUTION
# ---------------------------------------------------------------------

print("\n=== NDVI OBSERVATIONS BY YEAR ===")

year_counts = (
    dates
    .dt.year
    .value_counts()
    .sort_index()
)

print(year_counts.to_string())

# ---------------------------------------------------------------------
# CELL COVERAGE
# ---------------------------------------------------------------------

print("\n=== CELL COVERAGE ===")

cells = (
    ndvi["ID"]
    .astype(str)
    .str.strip()
)

print(f"Unique cells: {cells.nunique():,}")

# ---------------------------------------------------------------------
# DATE COUNT PER CELL
# ---------------------------------------------------------------------

print("\n=== TEMPORAL OBSERVATIONS PER CELL ===")

per_cell = (
    pd.DataFrame({
        "grid_cell_id": cells,
        "date": dates,
    })
    .groupby("grid_cell_id")
    .agg(
        observation_count=("date", "size"),
        unique_dates=("date", "nunique"),
        first_date=("date", "min"),
        last_date=("date", "max"),
    )
    .reset_index()
)

print(
    per_cell
    .sort_values("grid_cell_id")
    .to_string(index=False)
)

# ---------------------------------------------------------------------
# CHECK CADENCE
# ---------------------------------------------------------------------

print("\n=== TEMPORAL CADENCE ===")

date_diffs = (
    unique_dates
    .diff()
    .dropna()
    .dt.days
)

print(
    date_diffs
    .value_counts()
    .sort_index()
    .to_string()
)

# ---------------------------------------------------------------------
# FINAL DIAGNOSTIC
# ---------------------------------------------------------------------

print("\n" + "=" * 80)
print("TEMPORAL RANGE INSPECTION COMPLETE")
print("=" * 80)

print(
    f"\nExisting task spans: "
    f"{unique_dates.min().date()} → {unique_dates.max().date()}"
)

print(
    f"Existing task contains {len(unique_dates)} unique dates."
)

print(
    "\nUse this information to construct the second AppEEARS task."
)

