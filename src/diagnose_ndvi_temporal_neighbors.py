from pathlib import Path
import pandas as pd


SCRIPT = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT.parent.parent

PA_PATH = PROJECT_ROOT / "data" / "processed" / "pseudo_absences_final.csv"

NDVI_PATH = (
    PROJECT_ROOT
    / "data"
    / "external"
    / "appeears_ndvi_pa_v2_gap_45cells"
    / "queleaguard-ndvi-pa-v2-gap-45cells-MOD13Q1-061-results.csv"
)


def main():
    print("=" * 80)
    print("QueleaGuard Milestone 4.5 - NDVI Temporal Neighborhood Diagnostic")
    print("=" * 80)

    # ---------------------------------------------------------------
    # LOAD PA
    # ---------------------------------------------------------------
    print("\n=== LOADING PSEUDO-ABSENCES ===")

    pa = pd.read_csv(PA_PATH)

    pa["join_date"] = (
        pd.to_datetime(
            pa["eventDate"],
            format="mixed",
            errors="coerce",
            utc=True,
        )
        .dt.normalize()
        .dt.tz_localize(None)
    )

    if pa["join_date"].isna().any():
        raise RuntimeError("PA date parsing failed.")

    print(f"PA records: {len(pa):,}")

    # ---------------------------------------------------------------
    # LOAD NDVI
    # ---------------------------------------------------------------
    print("\n=== LOADING APPEEARS NDVI ===")

    ndvi = pd.read_csv(NDVI_PATH)

    ndvi["join_date"] = pd.to_datetime(
        ndvi["Date"],
        format="mixed",
        errors="coerce",
    ).dt.normalize()

    if ndvi["join_date"].isna().any():
        raise RuntimeError("AppEEARS date parsing failed.")

    ndvi["ID"] = ndvi["ID"].astype(str)
    pa["grid_cell_id"] = pa["grid_cell_id"].astype(str)

    ndvi_value_col = "MOD13Q1_061__250m_16_days_NDVI"

    ndvi[ndvi_value_col] = pd.to_numeric(
        ndvi[ndvi_value_col],
        errors="coerce",
    )

    # ---------------------------------------------------------------
    # TASK CELLS
    # ---------------------------------------------------------------
    task_cells = set(ndvi["ID"].unique())

    pa_task = pa[
        pa["grid_cell_id"].isin(task_cells)
    ].copy()

    print(f"Cells in NDVI task: {len(task_cells)}")
    print(f"PA records in task cells: {len(pa_task):,}")

    # ---------------------------------------------------------------
    # UNIQUE COMPOSITE DATES
    # ---------------------------------------------------------------
    composite_dates = (
        ndvi["join_date"]
        .drop_duplicates()
        .sort_values()
        .reset_index(drop=True)
    )

    print(f"Unique MODIS composite dates: {len(composite_dates):,}")

    # ---------------------------------------------------------------
    # FIND TEMPORAL NEIGHBORS
    # ---------------------------------------------------------------
    print("\n=== FINDING TEMPORAL NEIGHBORS ===")

    records = []

    for _, pa_row in pa_task.iterrows():

        cell = pa_row["grid_cell_id"]
        event_date = pa_row["join_date"]

        before = composite_dates[
            composite_dates <= event_date
        ]

        after = composite_dates[
            composite_dates >= event_date
        ]

        previous_date = (
            before.iloc[-1]
            if len(before)
            else pd.NaT
        )

        next_date = (
            after.iloc[0]
            if len(after)
            else pd.NaT
        )

        previous_days = (
            (event_date - previous_date).days
            if pd.notna(previous_date)
            else None
        )

        next_days = (
            (next_date - event_date).days
            if pd.notna(next_date)
            else None
        )

        # -----------------------------------------------------------
        # GET NDVI VALUES FOR THE TWO CANDIDATE COMPOSITES
        # -----------------------------------------------------------
        previous_ndvi = None
        next_ndvi = None

        if pd.notna(previous_date):

            rows = ndvi[
                (ndvi["ID"] == cell)
                & (ndvi["join_date"] == previous_date)
            ]

            if not rows.empty:
                previous_ndvi = rows.iloc[0][ndvi_value_col]

        if pd.notna(next_date):

            rows = ndvi[
                (ndvi["ID"] == cell)
                & (ndvi["join_date"] == next_date)
            ]

            if not rows.empty:
                next_ndvi = rows.iloc[0][ndvi_value_col]

        records.append(
            {
                "grid_cell_id": cell,
                "eventDate": pa_row["eventDate"],
                "event_date": event_date,
                "previous_composite": previous_date,
                "previous_days": previous_days,
                "previous_ndvi": previous_ndvi,
                "next_composite": next_date,
                "next_days": next_days,
                "next_ndvi": next_ndvi,
            }
        )

    result = pd.DataFrame(records)

    # ---------------------------------------------------------------
    # DISPLAY SUMMARY
    # ---------------------------------------------------------------
    print("\n=== TEMPORAL DISTANCE SUMMARY ===")

    print(
        result[
            [
                "previous_days",
                "next_days",
            ]
        ].describe()
    )

    # ---------------------------------------------------------------
    # SHOW ALL EVENTS
    # ---------------------------------------------------------------
    print("\n=== ALL PA EVENTS WITH TEMPORAL NEIGHBORS ===")

    display_columns = [
        "grid_cell_id",
        "event_date",
        "previous_composite",
        "previous_days",
        "previous_ndvi",
        "next_composite",
        "next_days",
        "next_ndvi",
    ]

    print(
        result[
            display_columns
        ].to_string(index=False)
    )

    # ---------------------------------------------------------------
    # TEMPORAL DISTANCE CATEGORIES
    # ---------------------------------------------------------------
    result["nearest_days"] = result[
        ["previous_days", "next_days"]
    ].min(axis=1)

    print("\n=== NEAREST COMPOSITE DISTANCE DISTRIBUTION ===")

    print(
        result["nearest_days"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print("\n=== EVENTS WITH NEAREST COMPOSITE <= 8 DAYS ===")

    within_8 = result[
        result["nearest_days"] <= 8
    ]

    print(
        f"{len(within_8):,} / {len(result):,}"
    )

    print("\n=== EVENTS WITH NEAREST COMPOSITE <= 16 DAYS ===")

    within_16 = result[
        result["nearest_days"] <= 16
    ]

    print(
        f"{len(within_16):,} / {len(result):,}"
    )

    # ---------------------------------------------------------------
    # FILL VALUES
    # ---------------------------------------------------------------
    print("\n=== CANDIDATE NDVI FILL-VALUE CHECK ===")

    previous_fill = (
        result["previous_ndvi"] == -3000
    ).sum()

    next_fill = (
        result["next_ndvi"] == -3000
    ).sum()

    print(
        f"Previous composite = -3000: {previous_fill:,}"
    )

    print(
        f"Next composite = -3000:     {next_fill:,}"
    )

    # ---------------------------------------------------------------
    # FINAL
    # ---------------------------------------------------------------
    print("\n=== DIAGNOSTIC COMPLETE ===")
    print("NO FILES WERE MODIFIED.")


if __name__ == "__main__":
    main()
