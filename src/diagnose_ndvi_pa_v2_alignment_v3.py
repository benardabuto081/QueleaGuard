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
    print("QueleaGuard Milestone 4.5 - NDVI Event Alignment Diagnostic v3")
    print("=" * 80)

    # ------------------------------------------------------------------
    # LOAD PA DATA
    # ------------------------------------------------------------------
    print("\n=== LOADING CORRECTED PSEUDO-ABSENCES ===")

    pa = pd.read_csv(PA_PATH)

    print(f"PA records loaded: {len(pa):,}")

    # ------------------------------------------------------------------
    # PARSE PA DATES
    # ------------------------------------------------------------------
    print("\n=== NORMALIZING PA EVENT DATES ===")

    # IMPORTANT:
    # The micro-diagnostic proved format="mixed" successfully parses
    # all 133 PA eventDate values.
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

    failed = pa["join_date"].isna().sum()

    print(f"PA dates successfully parsed: {len(pa) - failed:,}")
    print(f"PA dates failed parsing:      {failed:,}")

    if failed:
        print("\nFAILED DATE VALUES:")
        print(pa.loc[pa["join_date"].isna(), ["grid_cell_id", "eventDate"]].to_string(index=False))
        raise RuntimeError("PA date parsing still has failures.")

    # ------------------------------------------------------------------
    # LOAD APPEEARS
    # ------------------------------------------------------------------
    print("\n=== LOADING RAW APPEEARS NDVI ===")

    ndvi = pd.read_csv(NDVI_PATH)

    print(f"Raw AppEEARS rows: {len(ndvi):,}")

    # ------------------------------------------------------------------
    # NORMALIZE APPEEARS DATES
    # ------------------------------------------------------------------
    print("\n=== NORMALIZING APPEEARS DATES ===")

    ndvi["join_date"] = pd.to_datetime(
        ndvi["Date"],
        format="mixed",
        errors="coerce",
    ).dt.normalize()

    failed_ndvi = ndvi["join_date"].isna().sum()

    print(f"AppEEARS dates successfully parsed: {len(ndvi) - failed_ndvi:,}")
    print(f"AppEEARS dates failed parsing:      {failed_ndvi:,}")

    if failed_ndvi:
        raise RuntimeError("AppEEARS date parsing failed.")

    # ------------------------------------------------------------------
    # CELL COVERAGE
    # ------------------------------------------------------------------
    print("\n=== NEW TASK CELL COVERAGE ===")

    task_cells = set(ndvi["ID"].dropna().astype(str))
    pa_cells = set(pa["grid_cell_id"].dropna().astype(str))

    print(f"Cells in AppEEARS task: {len(task_cells)}")
    print(f"Unique cells in corrected PA dataset: {len(pa_cells)}")

    pa_task = pa[pa["grid_cell_id"].astype(str).isin(task_cells)].copy()

    print(
        f"PA records belonging to these task cells: "
        f"{len(pa_task):,} / {len(pa):,}"
    )

    # ------------------------------------------------------------------
    # EXACT CELL + DATE MATCH
    # ------------------------------------------------------------------
    print("\n=== EXACT (CELL, CALENDAR DATE) ALIGNMENT ===")

    ndvi_keys = set(
        zip(
            ndvi["ID"].astype(str),
            ndvi["join_date"],
        )
    )

    pa_task["exact_match"] = [
        (str(cell), date) in ndvi_keys
        for cell, date in zip(
            pa_task["grid_cell_id"],
            pa_task["join_date"],
        )
    ]

    matched = int(pa_task["exact_match"].sum())
    unmatched = len(pa_task) - matched

    print(f"PA records in task cells:   {len(pa_task):,}")
    print(f"Exact cell+date matches:     {matched:,}")
    print(f"No exact cell+date match:    {unmatched:,}")

    # ------------------------------------------------------------------
    # UNMATCHED EVENTS
    # ------------------------------------------------------------------
    if unmatched:
        print("\n--- UNMATCHED PA EVENTS ---")

        unmatched_df = pa_task.loc[
            ~pa_task["exact_match"],
            [
                "grid_cell_id",
                "eventDate",
                "join_date",
            ],
        ].copy()

        print(unmatched_df.to_string(index=False))

    # ------------------------------------------------------------------
    # MATCHED EVENTS
    # ------------------------------------------------------------------
    if matched:
        print("\n--- MATCHED PA EVENTS ---")

        matched_df = pa_task.loc[
            pa_task["exact_match"],
            [
                "grid_cell_id",
                "eventDate",
                "join_date",
            ],
        ].copy()

        print(matched_df.to_string(index=False))

    # ------------------------------------------------------------------
    # NDVI QC
    # ------------------------------------------------------------------
    print("\n=== NDVI VALUE QC ===")

    ndvi_col = "MOD13Q1_061__250m_16_days_NDVI"

    ndvi_values = pd.to_numeric(
        ndvi[ndvi_col],
        errors="coerce",
    )

    fill_count = int((ndvi_values == -3000).sum())
    valid_count = int(
        ndvi_values.between(-1, 1, inclusive="both").sum()
    )

    outside_count = int(
        (~ndvi_values.between(-1, 1, inclusive="both")).sum()
    )

    print(f"Total AppEEARS observations: {len(ndvi_values):,}")
    print(f"NDVI fill values (-3000):    {fill_count:,}")
    print(f"Values within [-1, 1]:       {valid_count:,}")
    print(f"Values outside [-1, 1]:      {outside_count:,}")

    # ------------------------------------------------------------------
    # TEMPORAL COVERAGE
    # ------------------------------------------------------------------
    print("\n=== TEMPORAL COVERAGE ===")

    print(f"AppEEARS minimum date: {ndvi['join_date'].min().date()}")
    print(f"AppEEARS maximum date: {ndvi['join_date'].max().date()}")
    print(f"AppEEARS unique dates: {ndvi['join_date'].nunique():,}")

    # ------------------------------------------------------------------
    # RECORD ACCOUNTING
    # ------------------------------------------------------------------
    print("\n=== RECORD ACCOUNTING ===")

    outside_task = len(pa) - len(pa_task)

    print(f"Corrected PA records total:                 {len(pa):,}")
    print(f"PA records in the 45 new cells:              {len(pa_task):,}")
    print(f"Matched in this NDVI bundle:                {matched:,}")
    print(f"Unmatched in this NDVI bundle:              {unmatched:,}")
    print(
        f"PA records outside these 45 cells "
        f"(expected previous extraction):             {outside_task:,}"
    )

    # ------------------------------------------------------------------
    # DATE DISTRIBUTION DIAGNOSTIC
    # ------------------------------------------------------------------
    print("\n=== PA DATE vs APPEEARS COMPOSITE DIAGNOSTIC ===")

    available_dates = set(ndvi["join_date"])

    pa_task["date_exists_anywhere"] = pa_task["join_date"].isin(
        available_dates
    )

    date_exists = int(pa_task["date_exists_anywhere"].sum())

    print(
        f"PA event dates represented somewhere in AppEEARS: "
        f"{date_exists:,} / {len(pa_task):,}"
    )

    print(
        f"PA event dates NOT represented in AppEEARS composites: "
        f"{len(pa_task) - date_exists:,}"
    )

    # ------------------------------------------------------------------
    # FINAL
    # ------------------------------------------------------------------
    print("\n=== DIAGNOSTIC COMPLETE ===")
    print("NO FILES WERE MODIFIED.")


if __name__ == "__main__":
    main()
