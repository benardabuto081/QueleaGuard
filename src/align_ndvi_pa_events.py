from pathlib import Path
import pandas as pd
import numpy as np

print("=" * 80)
print("QueleaGuard Milestone 4.5 - CORRECTED NDVI PA EVENT ALIGNMENT")
print("=" * 80)

# ---------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

PA_FILE = ROOT / "data" / "processed" / "pseudo_absences_final.csv"

NDVI_DIR = (
    ROOT
    / "data"
    / "external"
    / "appeears_ndvi_pa_v2_gap_45cells"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "processed"
    / "ndvi_features_pseudo_absence.csv"
)

# ---------------------------------------------------------------------
# LOAD PSEUDO-ABSENCES
# ---------------------------------------------------------------------

print("\n=== LOADING CORRECTED PSEUDO-ABSENCES ===")

pa = pd.read_csv(PA_FILE)

print(f"PA records loaded: {len(pa):,}")

if "grid_cell_id" not in pa.columns:
    raise RuntimeError("pseudo_absences_final.csv has no 'grid_cell_id' column.")

if "eventDate" not in pa.columns:
    raise RuntimeError("pseudo_absences_final.csv has no 'eventDate' column.")

# ---------------------------------------------------------------------
# ROBUST DATE NORMALIZATION
#
# IMPORTANT:
# The PA dataset contains mixed date formats:
#   2015-12-31
#   2024-03-14T10:40
#   2026-03-01T09:17:17
#   2022-07-19T08:02:34.848Z
#
# format='mixed' is therefore intentional.
# We only need the calendar date for MODIS composite alignment.
# ---------------------------------------------------------------------

print("\n=== NORMALIZING PA EVENT DATES ===")

pa["_event_datetime"] = pd.to_datetime(
    pa["eventDate"],
    format="mixed",
    errors="coerce",
    utc=True,
)

pa["_event_date"] = pa["_event_datetime"].dt.normalize().dt.tz_localize(None)

failed = pa["_event_date"].isna()

print(f"PA dates successfully parsed: {(~failed).sum():,}")
print(f"PA dates failed parsing:      {failed.sum():,}")

if failed.any():
    print("\nFailed PA dates:")
    print(pa.loc[failed, ["grid_cell_id", "eventDate"]].to_string(index=False))

    raise RuntimeError(
        "Some PA event dates could not be parsed. "
        "This should not happen with format='mixed'."
    )

# ---------------------------------------------------------------------
# LOCATE APPEEARS CSV
# ---------------------------------------------------------------------

print("\n=== LOCATING APPEEARS NDVI BUNDLE ===")
print(f"Searching:\n{NDVI_DIR}")

csv_files = sorted(NDVI_DIR.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError(
        f"No CSV files found under:\n{NDVI_DIR}"
    )

print("\nCSV files discovered:")
for f in csv_files:
    print(f"  {f}")

# Prefer MOD13Q1 results CSV
preferred = [
    f for f in csv_files
    if "MOD13Q1" in f.name.upper()
    and "RESULT" in f.name.upper()
]

if preferred:
    ndvi_file = preferred[0]
else:
    ndvi_file = csv_files[0]

print("\nSelected AppEEARS CSV:")
print(f"  {ndvi_file}")

# ---------------------------------------------------------------------
# LOAD APPEEARS
# ---------------------------------------------------------------------

print("\n=== LOADING APPEEARS NDVI ===")

ndvi = pd.read_csv(ndvi_file)

print(f"Raw AppEEARS rows: {len(ndvi):,}")
print(f"Raw AppEEARS columns: {len(ndvi.columns):,}")

# Required columns
required = {
    "ID",
    "Date",
    "MOD13Q1_061__250m_16_days_NDVI",
}

missing = required - set(ndvi.columns)

if missing:
    raise RuntimeError(
        "AppEEARS CSV is missing required columns: "
        + ", ".join(sorted(missing))
    )

# ---------------------------------------------------------------------
# NORMALIZE APPEEARS KEYS
# ---------------------------------------------------------------------

print("\n=== NORMALIZING APPEEARS KEYS ===")

ndvi["grid_cell_id"] = ndvi["ID"].astype(str).str.strip()

ndvi["_ndvi_datetime"] = pd.to_datetime(
    ndvi["Date"],
    format="mixed",
    errors="coerce",
    utc=True,
)

ndvi["_ndvi_date"] = (
    ndvi["_ndvi_datetime"]
    .dt.normalize()
    .dt.tz_localize(None)
)

ndvi_failed = ndvi["_ndvi_date"].isna()

print(
    f"AppEEARS dates successfully parsed: "
    f"{(~ndvi_failed).sum():,}"
)
print(
    f"AppEEARS dates failed parsing:      "
    f"{ndvi_failed.sum():,}"
)

if ndvi_failed.any():
    raise RuntimeError(
        "Some AppEEARS dates could not be parsed."
    )

# ---------------------------------------------------------------------
# NDVI VALUE NORMALIZATION
#
# MOD13Q1 NDVI uses scale factor 0.0001.
# Fill value -3000 becomes -0.3000 and must NOT be treated as valid NDVI.
# ---------------------------------------------------------------------

NDVI_COLUMN = "MOD13Q1_061__250m_16_days_NDVI"

ndvi["ndvi_raw"] = pd.to_numeric(
    ndvi[NDVI_COLUMN],
    errors="coerce",
)

# MODIS fill value
ndvi["ndvi"] = ndvi["ndvi_raw"].copy()

fill_mask = ndvi["ndvi_raw"] == -3000

ndvi.loc[fill_mask, "ndvi"] = np.nan

print("\n=== NDVI VALUE QC ===")
print(f"Total AppEEARS observations: {len(ndvi):,}")
print(f"MODIS fill values (-3000):   {fill_mask.sum():,}")
print(
    f"Valid NDVI observations:     "
    f"{ndvi['ndvi'].notna().sum():,}"
)

# ---------------------------------------------------------------------
# TASK COVERAGE
# ---------------------------------------------------------------------

task_cells = set(ndvi["grid_cell_id"].unique())

pa_cells = set(pa["grid_cell_id"].astype(str))

pa["grid_cell_id"] = pa["grid_cell_id"].astype(str)

in_task = pa["grid_cell_id"].isin(task_cells)

print("\n=== TASK COVERAGE ===")
print(f"Cells in AppEEARS task: {len(task_cells):,}")
print(f"Unique cells in PA dataset: {pa['grid_cell_id'].nunique():,}")
print(
    f"PA records belonging to this task: "
    f"{in_task.sum():,} / {len(pa):,}"
)

pa_task = pa.loc[in_task].copy()

if pa_task.empty:
    raise RuntimeError(
        "No pseudo-absence records belong to the AppEEARS task cells."
    )

# ---------------------------------------------------------------------
# BUILD CELL/TIME INDEX
# ---------------------------------------------------------------------

print("\n=== BUILDING TEMPORAL NDVI INDEX ===")

ndvi_task = ndvi[
    ndvi["grid_cell_id"].isin(task_cells)
].copy()

duplicates = ndvi_task.duplicated(
    subset=["grid_cell_id", "_ndvi_date"]
).sum()

print(f"Duplicate cell/date observations: {duplicates:,}")

if duplicates:
    raise RuntimeError(
        "Duplicate cell/date observations found. "
        "Cannot safely perform temporal alignment."
    )

# Sort chronologically
ndvi_task = ndvi_task.sort_values(
    ["grid_cell_id", "_ndvi_date"]
).reset_index(drop=True)

# ---------------------------------------------------------------------
# TEMPORAL ALIGNMENT
#
# We DO NOT use a global date join.
#
# For every PA event:
#   1. restrict to the same grid cell
#   2. find nearest MODIS composite date
#   3. choose nearest previous/next observation
#   4. reject if nearest distance > 16 days
#
# This prevents accidentally assigning NDVI from another cell/year.
# ---------------------------------------------------------------------

print("\n=== TEMPORAL ALIGNMENT ===")

records = []

for _, pa_row in pa_task.iterrows():

    cell = pa_row["grid_cell_id"]
    event_date = pa_row["_event_date"]

    cell_ndvi = ndvi_task[
        ndvi_task["grid_cell_id"] == cell
    ].copy()

    if cell_ndvi.empty:
        continue

    dates = cell_ndvi["_ndvi_date"].values

    # Convert to integer nanoseconds for efficient nearest-date search
    event_ns = event_date.to_datetime64().astype("datetime64[ns]").astype("int64")
    date_ns = dates.astype("datetime64[ns]").astype("int64")

    idx = np.searchsorted(date_ns, event_ns)

    candidates = []

    if idx > 0:
        candidates.append(idx - 1)

    if idx < len(date_ns):
        candidates.append(idx)

    if not candidates:
        continue

    # Choose nearest candidate
    best_idx = min(
        candidates,
        key=lambda i: abs(date_ns[i] - event_ns)
    )

    best = cell_ndvi.iloc[best_idx]

    aligned_date = best["_ndvi_date"]

    distance_days = abs(
        (aligned_date - event_date).days
    )

    # Reject implausibly distant observations
    if distance_days > 16:
        continue

    if aligned_date < event_date:
        alignment = "previous"
    elif aligned_date > event_date:
        alignment = "next"
    else:
        alignment = "exact"

    records.append(
        {
            "grid_cell_id": cell,
            "eventDate": pa_row["eventDate"],
            "event_date": event_date,
            "ndvi_aligned_date": aligned_date,
            "ndvi": best["ndvi"],
            "ndvi_raw": best["ndvi_raw"],
            "ndvi_temporal_distance_days": distance_days,
            "ndvi_temporal_alignment": alignment,
        }
    )

aligned = pd.DataFrame(records)

# ---------------------------------------------------------------------
# QC
# ---------------------------------------------------------------------

print("\n=== ALIGNMENT QC ===")

print(
    f"PA records in task:             "
    f"{len(pa_task):,}"
)

print(
    f"Records with aligned NDVI:      "
    f"{len(aligned):,}"
)

print(
    f"Records without aligned NDVI:   "
    f"{len(pa_task) - len(aligned):,}"
)

if not aligned.empty:

    print(
        f"Maximum temporal distance:     "
        f"{aligned['ndvi_temporal_distance_days'].max():,} days"
    )

    print(
        f"Median temporal distance:      "
        f"{aligned['ndvi_temporal_distance_days'].median():.1f} days"
    )

    print("\nTemporal distance distribution:")
    print(
        aligned[
            "ndvi_temporal_distance_days"
        ].value_counts().sort_index().to_string()
    )

# ---------------------------------------------------------------------
# SAMPLE
# ---------------------------------------------------------------------

print("\n=== SAMPLE ALIGNMENTS ===")

if not aligned.empty:
    print(
        aligned[
            [
                "grid_cell_id",
                "eventDate",
                "ndvi_aligned_date",
                "ndvi",
                "ndvi_temporal_distance_days",
                "ndvi_temporal_alignment",
            ]
        ]
        .sort_values(["grid_cell_id", "eventDate"])
        .head(20)
        .to_string(index=False)
    )

# ---------------------------------------------------------------------
# SAVE
# ---------------------------------------------------------------------

print("\n=== SAVING ===")

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

aligned.to_csv(
    OUTPUT_FILE,
    index=False
)

print("Output written to:")
print(f"  {OUTPUT_FILE}")

print(f"Rows written: {len(aligned):,}")

print("\n" + "=" * 80)
print("CORRECTED NDVI PA EVENT ALIGNMENT COMPLETE")
print("=" * 80)


