"""
Milestone 4.5 (Stage 4) - NDVI event alignment diagnostic.

READ-ONLY.

Purpose:
    Determine whether every corrected pseudo-absence event has an exact
    corresponding MODIS NDVI observation for its grid cell and event date.

No NDVI values are transformed.
No files are modified.
"""

import pandas as pd

PA_PATH = "data/processed/pseudo_absences_final.csv"

NDVI_PATH = (
    "data/external/appeears_ndvi_pa_v2_gap_45cells/"
    "queleaguard-ndvi-pa-v2-gap-45cells-MOD13Q1-061-results.csv"
)

NDVI_COLUMN = "MOD13Q1_061__250m_16_days_NDVI"


def main():

    print("=" * 80)
    print("QueleaGuard Milestone 4.5 - NDVI Event Alignment Diagnostic")
    print("=" * 80)

    # ------------------------------------------------------------------
    # Load corrected pseudo-absence records
    # ------------------------------------------------------------------

    print("\n=== LOADING CORRECTED PSEUDO-ABSENCES ===")

    pa = pd.read_csv(PA_PATH)

    print(f"PA records loaded: {len(pa)}")

    print("\nPA columns:")
    for col in pa.columns:
        print(f"  {repr(col)}")

    # We expect the corrected set to contain 133 records.
    assert len(pa) == 133, (
        f"Expected exactly 133 corrected pseudo-absence records, "
        f"found {len(pa)}"
    )

    # ------------------------------------------------------------------
    # Identify required columns
    # ------------------------------------------------------------------

    required_pa = ["grid_cell_id", "eventDate"]

    missing_pa = [c for c in required_pa if c not in pa.columns]

    if missing_pa:
        raise RuntimeError(
            f"Required PA columns missing: {missing_pa}"
        )

    # ------------------------------------------------------------------
    # Load raw AppEEARS results
    # ------------------------------------------------------------------

    print("\n=== LOADING RAW APPEEARS NDVI ===")

    ndvi = pd.read_csv(NDVI_PATH)

    print(f"Raw AppEEARS rows: {len(ndvi):,}")
    print(f"Raw AppEEARS columns: {len(ndvi.columns)}")

    required_ndvi = ["ID", "Date", NDVI_COLUMN]

    missing_ndvi = [c for c in required_ndvi if c not in ndvi.columns]

    if missing_ndvi:
        raise RuntimeError(
            f"Required AppEEARS columns missing: {missing_ndvi}"
        )

    # ------------------------------------------------------------------
    # Normalize keys ONLY
    # ------------------------------------------------------------------

    print("\n=== NORMALIZING JOIN KEYS ===")

    pa["_cell"] = pa["grid_cell_id"].astype(str).str.strip()
    pa["_date"] = pd.to_datetime(
        pa["eventDate"],
        errors="coerce"
    ).dt.normalize()

    ndvi["_cell"] = ndvi["ID"].astype(str).str.strip()
    ndvi["_date"] = pd.to_datetime(
        ndvi["Date"],
        errors="coerce"
    ).dt.normalize()

    if pa["_date"].isna().any():
        bad = pa.loc[pa["_date"].isna(), ["grid_cell_id", "eventDate"]]
        raise RuntimeError(
            "One or more PA event dates failed parsing:\n"
            + bad.to_string(index=False)
        )

    if ndvi["_date"].isna().any():
        raise RuntimeError(
            "One or more AppEEARS dates failed parsing."
        )

    # ------------------------------------------------------------------
    # Check uniqueness of AppEEARS cell/date observations
    # ------------------------------------------------------------------

    print("\n=== APP EEARS CELL/DATE UNIQUENESS ===")

    duplicate_mask = ndvi.duplicated(
        subset=["_cell", "_date"],
        keep=False
    )

    duplicate_count = duplicate_mask.sum()

    print(f"Duplicate cell/date rows: {duplicate_count}")

    if duplicate_count:
        print("\nDUPLICATE EXAMPLES:")
        print(
            ndvi.loc[
                duplicate_mask,
                ["ID", "Date", NDVI_COLUMN]
            ].head(20).to_string(index=False)
        )

        raise RuntimeError(
            "AppEEARS contains duplicate cell/date observations. "
            "STOP before extraction."
        )

    # ------------------------------------------------------------------
    # Prepare the exact event-level lookup
    # ------------------------------------------------------------------

    lookup = ndvi[
        ["_cell", "_date", NDVI_COLUMN]
    ].copy()

    lookup = lookup.rename(
        columns={
            NDVI_COLUMN: "_raw_ndvi"
        }
    )

    # ------------------------------------------------------------------
    # Join PA events to NDVI
    # ------------------------------------------------------------------

    print("\n=== MATCHING PA EVENTS TO NDVI ===")

    merged = pa.merge(
        lookup,
        on=["_cell", "_date"],
        how="left",
        indicator=True
    )

    matched = merged["_merge"].eq("both")
    unmatched = merged["_merge"].eq("left_only")

    print(f"Total PA records:       {len(merged)}")
    print(f"Exact cell/date match:  {matched.sum()}")
    print(f"Unmatched:              {unmatched.sum()}")

    # ------------------------------------------------------------------
    # Raw NDVI classification
    # ------------------------------------------------------------------

    print("\n=== NDVI STATUS AT PA EVENT DATES ===")

    raw = pd.to_numeric(
        merged["_raw_ndvi"],
        errors="coerce"
    )

    valid_ndvi = (
        matched
        & raw.notna()
        & (raw >= -1)
        & (raw <= 1)
    )

    fill_ndvi = matched & raw.eq(-3000)

    unexpected = (
        matched
        & raw.notna()
        & ~raw.eq(-3000)
        & ((raw < -1) | (raw > 1))
    )

    missing_raw = matched & raw.isna()

    print(f"Matched + valid NDVI [-1,1]: {valid_ndvi.sum()}")
    print(f"Matched + -3000 fill:        {fill_ndvi.sum()}")
    print(f"Matched + missing raw:       {missing_raw.sum()}")
    print(f"Matched + unexpected range:  {unexpected.sum()}")

    # ------------------------------------------------------------------
    # Percentages
    # ------------------------------------------------------------------

    print("\n=== PERCENTAGES ===")

    total = len(merged)

    print(
        f"Exact event match: "
        f"{matched.sum()}/{total} "
        f"({matched.mean() * 100:.2f}%)"
    )

    print(
        f"Valid NDVI: "
        f"{valid_ndvi.sum()}/{total} "
        f"({valid_ndvi.mean() * 100:.2f}%)"
    )

    print(
        f"Fill (-3000): "
        f"{fill_ndvi.sum()}/{total} "
        f"({fill_ndvi.mean() * 100:.2f}%)"
    )

    print(
        f"Unmatched: "
        f"{unmatched.sum()}/{total} "
        f"({unmatched.mean() * 100:.2f}%)"
    )

    # ------------------------------------------------------------------
    # Unmatched records
    # ------------------------------------------------------------------

    if unmatched.any():

        print("\n=== UNMATCHED PA RECORDS ===")

        cols = [
            "grid_cell_id",
            "eventDate",
        ]

        print(
            merged.loc[
                unmatched,
                cols
            ].to_string(index=False)
        )

    # ------------------------------------------------------------------
    # Fill-value records
    # ------------------------------------------------------------------

    if fill_ndvi.any():

        print("\n=== PA EVENTS WITH -3000 FILL ===")

        cols = [
            "grid_cell_id",
            "eventDate",
            "_raw_ndvi",
        ]

        print(
            merged.loc[
                fill_ndvi,
                cols
            ].to_string(index=False)
        )

    # ------------------------------------------------------------------
    # Unexpected values
    # ------------------------------------------------------------------

    if unexpected.any():

        print("\n=== UNEXPECTED OUT-OF-RANGE VALUES ===")

        cols = [
            "grid_cell_id",
            "eventDate",
            "_raw_ndvi",
        ]

        print(
            merged.loc[
                unexpected,
                cols
            ].to_string(index=False)
        )

        raise RuntimeError(
            "Unexpected NDVI values found at PA event dates. "
            "STOP before extraction."
        )

    # ------------------------------------------------------------------
    # Final checkpoint
    # ------------------------------------------------------------------

    print("\n" + "=" * 80)
    print("EVENT ALIGNMENT DIAGNOSTIC COMPLETE")
    print("=" * 80)

    print("\nNO FILES WERE MODIFIED.")


if __name__ == "__main__":
    main()
