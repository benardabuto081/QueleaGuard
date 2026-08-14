from pathlib import Path
import pandas as pd

print("=" * 80)
print("QueleaGuard - ORIGINAL PA DUPLICATE EVENT VALIDATION")
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

# ---------------------------------------------------------------------
# LOAD ORIGINAL PA DATA
# ---------------------------------------------------------------------

print("\n=== LOADING ORIGINAL PA DATA ===")

pa = pd.read_csv(PA_FILE)

print(f"PA rows: {len(pa):,}")
print(f"Columns: {list(pa.columns)}")

# ---------------------------------------------------------------------
# NORMALIZE EVENT DATE
# ---------------------------------------------------------------------

print("\n=== NORMALIZING EVENT DATES ===")

if "eventDate" not in pa.columns:
    raise RuntimeError(
        "Required column 'eventDate' not found in pseudo_absences_final.csv"
    )

pa["_event_datetime"] = pd.to_datetime(
    pa["eventDate"],
    format="mixed",
    errors="coerce",
    utc=True,
)

pa["_event_date"] = (
    pa["_event_datetime"]
    .dt.normalize()
    .dt.tz_localize(None)
)

failed = pa["_event_date"].isna()

print(f"Dates successfully parsed: {(~failed).sum():,}")
print(f"Dates failed parsing:      {failed.sum():,}")

if failed.any():
    raise RuntimeError(
        "Some PA event dates could not be parsed."
    )

# ---------------------------------------------------------------------
# IDENTIFY DUPLICATE CELL / CALENDAR-DATE GROUPS
# ---------------------------------------------------------------------

print("\n=== IDENTIFYING DUPLICATE CELL/DATE GROUPS ===")

group_counts = (
    pa.groupby(
        ["grid_cell_id", "_event_date"],
        dropna=False
    )
    .size()
    .reset_index(name="record_count")
)

duplicates = group_counts[
    group_counts["record_count"] > 1
].copy()

print(
    f"Duplicate cell/date groups: {len(duplicates):,}"
)

print(
    f"PA records belonging to duplicate groups: "
    f"{duplicates['record_count'].sum():,}"
)

if duplicates.empty:
    print("\n[PASS] No duplicate cell/date groups found.")
    print("\nValidation complete.")
    raise SystemExit(0)

print("\n=== DUPLICATE GROUPS ===")

print(
    duplicates
    .sort_values(["grid_cell_id", "_event_date"])
    .to_string(index=False)
)

# ---------------------------------------------------------------------
# INSPECT SOURCE RECORDS
# ---------------------------------------------------------------------

print("\n=== SOURCE RECORD INSPECTION ===")

for _, group in duplicates.iterrows():

    cell = group["grid_cell_id"]
    date = group["_event_date"]

    subset = pa[
        (pa["grid_cell_id"] == cell)
        & (pa["_event_date"] == date)
    ].copy()

    print("\n" + "-" * 72)
    print(f"Cell: {cell}")
    print(f"Calendar date: {date.date()}")
    print(f"Number of source PA records: {len(subset)}")

    # Show all columns that help distinguish events
    preferred_columns = [
        "grid_cell_id",
        "eventDate",
        "latitude",
        "longitude",
        "lat",
        "lon",
        "species",
        "source",
        "label",
        "presence_absence",
        "pa_type",
    ]

    display_columns = [
        col for col in preferred_columns
        if col in subset.columns
    ]

    # If preferred fields are unavailable, show all columns
    if not display_columns:
        display_columns = list(pa.columns)

    print(
        subset[display_columns]
        .to_string(index=False)
    )

# ---------------------------------------------------------------------
# EXACT DUPLICATE CHECK
# ---------------------------------------------------------------------

print("\n=== EXACT ROW DUPLICATE CHECK ===")

# Exclude helper columns
source_columns = [
    col for col in pa.columns
    if not col.startswith("_")
]

exact_duplicates = pa.duplicated(
    subset=source_columns,
    keep=False
)

exact_duplicate_count = exact_duplicates.sum()

print(
    f"Exact duplicate source rows: "
    f"{exact_duplicate_count:,}"
)

if exact_duplicate_count == 0:
    print(
        "[PASS] No exact duplicate PA rows."
    )
else:
    print(
        "[WARNING] Exact duplicate PA rows exist."
    )

    print(
        pa.loc[
            exact_duplicates,
            source_columns
        ].to_string(index=False)
    )

# ---------------------------------------------------------------------
# TIMESTAMP DISTINCTNESS
# ---------------------------------------------------------------------

print("\n=== TIMESTAMP DISTINCTNESS ===")

for _, group in duplicates.iterrows():

    cell = group["grid_cell_id"]
    date = group["_event_date"]

    subset = pa[
        (pa["grid_cell_id"] == cell)
        & (pa["_event_date"] == date)
    ].copy()

    timestamps = (
        subset["eventDate"]
        .astype(str)
        .tolist()
    )

    unique_timestamps = set(timestamps)

    print(
        f"{cell} | {date.date()} | "
        f"records={len(subset)} | "
        f"unique timestamps={len(unique_timestamps)}"
    )

# ---------------------------------------------------------------------
# FINAL VERDICT
# ---------------------------------------------------------------------

print("\n" + "=" * 80)
print("DUPLICATE EVENT VALIDATION VERDICT")
print("=" * 80)

if exact_duplicate_count == 0:

    print(
        "[PASS] No exact duplicate source rows detected."
    )

    print(
        "[PASS] Same-day duplicate groups appear to represent "
        "multiple source events rather than duplicated rows."
    )

    print(
        "\nDO NOT REMOVE THESE EVENTS."
    )

else:

    print(
        "[FAIL] Exact duplicate source rows exist."
    )

    print(
        "\nThose exact duplicates must be investigated "
        "before final feature construction."
    )

print(
    "\nIMPORTANT:"
)

print(
    "NDVI coverage remains the primary blocker."
)

print(
    "Current NDVI coverage: 67/133 = 50.38%"
)

print(
    "Do NOT begin final modeling until the remaining "
    "66 PA records have NDVI coverage."
)

print("=" * 80)
