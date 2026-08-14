"""
Milestone 4.5 - NDVI Event Alignment Diagnostic v2

Purpose:
    Diagnose temporal/spatial alignment between the corrected 133-record
    pseudo-absence dataset and the newly downloaded 45-cell AppEEARS NDVI
    extraction.

Important:
    - The source PA eventDate is NEVER modified.
    - ISO timestamps are normalized to calendar dates ONLY for the join key.
    - This diagnostic does not create or modify modeling data.
"""

from pathlib import Path
import pandas as pd


PA_PATH = Path("data/processed/pseudo_absences_final.csv")

NDVI_PATH = Path(
    "data/external/appeears_ndvi_pa_v2_gap_45cells/"
    "queleaguard-ndvi-pa-v2-gap-45cells-MOD13Q1-061-results.csv"
)

NDVI_COL = "MOD13Q1_061__250m_16_days_NDVI"


def parse_calendar_date(series, name):
    """
    Parse mixed ISO date/date-time representations and return calendar dates.
    This is ONLY a diagnostic/join representation.
    """
    parsed = pd.to_datetime(series, errors="coerce", utc=True)

    failed = parsed.isna()

    if failed.any():
        print(f"\nWARNING: {failed.sum()} {name} values failed parsing:")
        print(series.loc[failed].to_string(index=False))

    return parsed.dt.date


def main():
    print("=" * 80)
    print("QueleaGuard Milestone 4.5 - NDVI Event Alignment Diagnostic v2")
    print("=" * 80)

    # ------------------------------------------------------------------
    # LOAD PA
    # ------------------------------------------------------------------
    print("\n=== LOADING CORRECTED PSEUDO-ABSENCES ===")

    pa = pd.read_csv(PA_PATH)

    print(f"PA records loaded: {len(pa)}")

    required_pa = {
        "grid_cell_id",
        "eventDate",
        "presence",
    }

    missing = required_pa - set(pa.columns)

    if missing:
        raise RuntimeError(
            f"Corrected PA dataset is missing required columns: {sorted(missing)}"
        )

    # Preserve original eventDate exactly.
    pa["eventDate_original"] = pa["eventDate"].astype(str)

    # Calendar date ONLY for joining.
    pa["join_date"] = parse_calendar_date(
        pa["eventDate"],
        "PA eventDate"
    )

    # ------------------------------------------------------------------
    # LOAD APP EEARS
    # ------------------------------------------------------------------
    print("\n=== LOADING RAW APPEEARS NDVI ===")

    ndvi = pd.read_csv(NDVI_PATH)

    print(f"Raw AppEEARS rows: {len(ndvi)}")

    required_ndvi = {
        "ID",
        "Date",
        NDVI_COL,
    }

    missing = required_ndvi - set(ndvi.columns)

    if missing:
        raise RuntimeError(
            f"AppEEARS results missing required columns: {sorted(missing)}"
        )

    # ------------------------------------------------------------------
    # NORMALIZE APPEEARS DATE
    # ------------------------------------------------------------------
    print("\n=== NORMALIZING APPEEARS DATES ===")

    ndvi["join_date"] = parse_calendar_date(
        ndvi["Date"],
        "AppEEARS Date"
    )

    if ndvi["join_date"].isna().any():
        raise RuntimeError(
            "AppEEARS contains unparseable dates. "
            "Stop before alignment."
        )

    # ------------------------------------------------------------------
    # CHECK NEW TASK COVERAGE
    # ------------------------------------------------------------------
    print("\n=== NEW TASK CELL COVERAGE ===")

    task_cells = sorted(ndvi["ID"].dropna().unique())
    pa_cells = sorted(pa["grid_cell_id"].dropna().unique())

    print(f"Cells in AppEEARS task: {len(task_cells)}")
    print(f"Unique cells in corrected PA dataset: {len(pa_cells)}")

    pa_in_task = pa[pa["grid_cell_id"].isin(task_cells)].copy()

    print(
        f"PA records belonging to these 45 extracted cells: "
        f"{len(pa_in_task)} / {len(pa)}"
    )

    # ------------------------------------------------------------------
    # EXACT EVENT ALIGNMENT
    # ------------------------------------------------------------------
    print("\n=== EXACT (CELL, CALENDAR DATE) ALIGNMENT ===")

    ndvi_keys = (
        ndvi[["ID", "join_date"]]
        .drop_duplicates()
        .rename(
            columns={
                "ID": "grid_cell_id"
            }
        )
    )

    pa_check = pa_in_task.merge(
        ndvi_keys,
        on=["grid_cell_id", "join_date"],
        how="left",
        indicator=True,
    )

    matched = pa_check["_merge"].eq("both")
    unmatched = ~matched

    print(f"PA records in task cells: {len(pa_check)}")
    print(f"Exact cell+date matches: {matched.sum()}")
    print(f"No exact cell+date match: {unmatched.sum()}")

    if unmatched.any():
        print("\n--- UNMATCHED PA EVENTS ---")

        cols = [
            "grid_cell_id",
            "eventDate_original",
            "join_date",
        ]

        print(
            pa_check.loc[unmatched, cols]
            .sort_values(["grid_cell_id", "join_date"])
            .to_string(index=False)
        )

    # ------------------------------------------------------------------
    # NDVI VALUE QC
    # ------------------------------------------------------------------
    print("\n=== NDVI VALUE QC ===")

    values = pd.to_numeric(
        ndvi[NDVI_COL],
        errors="coerce"
    )

    fill_mask = values.eq(-3000)

    valid_range = values.between(-1, 1)

    print(f"Total AppEEARS observations: {len(ndvi)}")
    print(f"NDVI fill values (-3000): {fill_mask.sum()}")
    print(
        f"Values within expected NDVI range [-1, 1]: "
        f"{valid_range.sum()}"
    )
    print(
        f"Values outside [-1, 1]: "
        f"{(~valid_range).sum()}"
    )

    if (~valid_range & ~fill_mask).any():
        print("\nWARNING: Non-fill values outside [-1, 1]:")
        print(
            ndvi.loc[
                ~valid_range & ~fill_mask,
                [NDVI_COL]
            ]
            .drop_duplicates()
            .sort_values(NDVI_COL)
            .to_string(index=False)
        )

    # ------------------------------------------------------------------
    # DATE COVERAGE
    # ------------------------------------------------------------------
    print("\n=== TEMPORAL COVERAGE ===")

    print(
        f"AppEEARS minimum date: "
        f"{ndvi['join_date'].min()}"
    )

    print(
        f"AppEEARS maximum date: "
        f"{ndvi['join_date'].max()}"
    )

    print(
        f"AppEEARS unique composite dates: "
        f"{ndvi['join_date'].nunique()}"
    )

    # ------------------------------------------------------------------
    # RECORD ACCOUNTING
    # ------------------------------------------------------------------
    print("\n=== RECORD ACCOUNTING ===")

    print(f"Corrected PA records total: {len(pa)}")
    print(f"PA records in the 45 new cells: {len(pa_in_task)}")
    print(f"Matched in this NDVI bundle: {matched.sum()}")
    print(f"Unmatched in this NDVI bundle: {unmatched.sum()}")

    outside_task = pa[~pa["grid_cell_id"].isin(task_cells)]

    print(
        f"PA records outside these 45 cells "
        f"(expected to be covered by previous NDVI extraction): "
        f"{len(outside_task)}"
    )

    print("\n=== DIAGNOSTIC COMPLETE ===")
    print("NO FILES WERE MODIFIED.")


if __name__ == "__main__":
    main()
