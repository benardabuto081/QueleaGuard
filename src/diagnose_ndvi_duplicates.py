from pathlib import Path
import pandas as pd

print("=" * 80)
print("QueleaGuard - NDVI PA DUPLICATE EVENT DIAGNOSTIC")
print("=" * 80)

ROOT = Path(__file__).resolve().parents[1]

NDVI_FILE = (
    ROOT
    / "data"
    / "processed"
    / "ndvi_features_pseudo_absence.csv"
)

# ---------------------------------------------------------------------
# LOAD
# ---------------------------------------------------------------------

print("\n=== LOADING NDVI OUTPUT ===")

ndvi = pd.read_csv(NDVI_FILE)

print(f"NDVI rows: {len(ndvi):,}")
print(f"Columns: {list(ndvi.columns)}")

# ---------------------------------------------------------------------
# NORMALIZE EVENT DATE
# ---------------------------------------------------------------------

print("\n=== NORMALIZING EVENT DATES ===")

if "event_date" not in ndvi.columns:
    raise RuntimeError(
        "Expected 'event_date' column is missing."
    )

ndvi["event_date_normalized"] = pd.to_datetime(
    ndvi["event_date"],
    format="mixed",
    errors="coerce",
    utc=True,
).dt.normalize().dt.tz_localize(None)

failed = ndvi["event_date_normalized"].isna()

print(
    f"Dates successfully parsed: {(~failed).sum():,}"
)
print(
    f"Dates failed parsing:      {failed.sum():,}"
)

if failed.any():
    print("\nFailed event dates:")
    print(
        ndvi.loc[
            failed,
            ["grid_cell_id", "event_date"]
        ].to_string(index=False)
    )
    raise RuntimeError(
        "Some event dates could not be parsed."
    )

# ---------------------------------------------------------------------
# DUPLICATE DETECTION
# ---------------------------------------------------------------------

print("\n=== DUPLICATE SUMMARY ===")

duplicate_mask = ndvi.duplicated(
    subset=[
        "grid_cell_id",
        "event_date_normalized"
    ],
    keep=False,
)

duplicate_rows = ndvi.loc[
    duplicate_mask
].copy()

duplicate_groups = (
    duplicate_rows
    .groupby(
        [
            "grid_cell_id",
            "event_date_normalized"
        ]
    )
    .size()
)

print(
    f"Total NDVI rows:              {len(ndvi):,}"
)

print(
    f"Rows involved in duplicates:  "
    f"{len(duplicate_rows):,}"
)

print(
    f"Duplicate groups:             "
    f"{len(duplicate_groups):,}"
)

# ---------------------------------------------------------------------
# DISPLAY DUPLICATES
# ---------------------------------------------------------------------

if duplicate_rows.empty:

    print(
        "\n[PASS] No duplicate cell/event-date "
        "records found."
    )

else:

    print("\n=== DUPLICATE RECORDS ===")

    display_columns = [
        "grid_cell_id",
        "eventDate",
        "event_date",
        "ndvi_aligned_date",
        "ndvi",
        "ndvi_raw",
        "ndvi_temporal_distance_days",
        "ndvi_temporal_alignment",
    ]

    display_columns = [
        c
        for c in display_columns
        if c in duplicate_rows.columns
    ]

    duplicate_rows = duplicate_rows.sort_values(
        [
            "grid_cell_id",
            "event_date_normalized"
        ]
    )

    print(
        duplicate_rows[
            display_columns
        ].to_string(index=False)
    )

    # -----------------------------------------------------------------
    # GROUP COUNTS
    # -----------------------------------------------------------------

    print("\n=== DUPLICATE GROUP COUNTS ===")

    group_table = (
        duplicate_groups
        .reset_index(name="record_count")
        .sort_values(
            [
                "grid_cell_id",
                "event_date_normalized"
            ]
        )
    )

    print(
        group_table.to_string(index=False)
    )

    # -----------------------------------------------------------------
    # INTERPRETATION
    # -----------------------------------------------------------------

    print("\n=== DUPLICATE GROUP INTERPRETATION ===")

    for _, group in group_table.iterrows():

        cell = group["grid_cell_id"]
        date = group["event_date_normalized"]
        count = group["record_count"]

        print("\n" + "-" * 70)
        print(
            f"Cell: {cell}"
        )
        print(
            f"Calendar date: {date.date()}"
        )
        print(
            f"Number of PA records: {count}"
        )

        records = duplicate_rows[
            (
                duplicate_rows["grid_cell_id"]
                == cell
            )
            &
            (
                duplicate_rows[
                    "event_date_normalized"
                ]
                == date
            )
        ]

        cols = [
            c
            for c in [
                "eventDate",
                "event_date",
                "ndvi_aligned_date",
                "ndvi",
                "ndvi_raw",
                "ndvi_temporal_distance_days",
                "ndvi_temporal_alignment",
            ]
            if c in records.columns
        ]

        print(
            records[cols].to_string(index=False)
        )

# ---------------------------------------------------------------------
# FINAL VERDICT
# ---------------------------------------------------------------------

print("\n" + "=" * 80)
print("DUPLICATE DIAGNOSTIC COMPLETE")
print("=" * 80)

if duplicate_rows.empty:

    print(
        "[PASS] No duplicate cell/event-date records."
    )

else:

    print(
        f"[WARNING] {len(duplicate_rows)} rows belong "
        f"to {len(duplicate_groups)} duplicate groups."
    )

    print(
        "\nThese records should NOT be deleted automatically."
    )

    print(
        "The next step is to determine whether they represent "
        "distinct PA events occurring on the same calendar date."
    )

print("=" * 80)
