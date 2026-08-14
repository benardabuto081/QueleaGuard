"""
Milestone 4.5 (Stage 3) - Diagnose raw AppEEARS NDVI results.

This script is READ-ONLY.
It does not alter the downloaded AppEEARS artifacts.

Purpose:
    Understand the exact structure, temporal coverage, point coverage,
    and raw value conventions before writing the extraction pipeline.
"""

import os
import pandas as pd

RESULTS_PATH = (
    "data/external/appeears_ndvi_pa_v2_gap_45cells/"
    "queleaguard-ndvi-pa-v2-gap-45cells-MOD13Q1-061-results.csv"
)

EXPECTED_CELLS = 45


def main():
    print("=" * 80)
    print("QueleaGuard Milestone 4.5 - Raw NDVI Diagnostic")
    print("=" * 80)

    print(f"\nResults file:")
    print(RESULTS_PATH)

    if not os.path.exists(RESULTS_PATH):
        raise FileNotFoundError(RESULTS_PATH)

    print(f"File size: {os.path.getsize(RESULTS_PATH):,} bytes")

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------

    df = pd.read_csv(RESULTS_PATH)

    print("\n=== BASIC STRUCTURE ===")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumn names:")
    for i, col in enumerate(df.columns, start=1):
        print(f"  {i:02d}. {repr(col)}")

    print("\nDtypes:")
    print(df.dtypes.to_string())

    # ------------------------------------------------------------------
    # Sample
    # ------------------------------------------------------------------

    print("\n=== FIRST 5 ROWS ===")
    print(df.head().to_string(index=False))

    # ------------------------------------------------------------------
    # Identify likely columns
    # ------------------------------------------------------------------

    print("\n=== COLUMN IDENTIFICATION ===")

    for col in df.columns:
        lower = col.lower()

        if any(x in lower for x in ["date", "time", "time"]):
            print(f"Possible temporal column: {col}")

        if any(x in lower for x in ["ndvi", "250m_16_days"]):
            print(f"Possible NDVI column: {col}")

        if lower in ["id", "point", "latitude", "longitude", "lat", "lon"]:
            print(f"Possible spatial/point column: {col}")

    # ------------------------------------------------------------------
    # Unique values / coverage
    # ------------------------------------------------------------------

    print("\n=== UNIQUE-VALUE SUMMARY ===")

    for col in df.columns:
        nunique = df[col].nunique(dropna=True)

        if nunique <= 60:
            print(f"{col}: {nunique} unique non-null values")

    # ------------------------------------------------------------------
    # Look for point/cell coverage
    # ------------------------------------------------------------------

    possible_id_cols = [
        col for col in df.columns
        if col.lower() in ["id", "point", "point_id", "identifier"]
    ]

    if possible_id_cols:
        for col in possible_id_cols:
            print(f"\n=== COVERAGE FOR {col} ===")
            values = df[col].dropna().unique()
            print(f"Unique values: {len(values)}")
            print(sorted(map(str, values))[:100])

    # ------------------------------------------------------------------
    # Date diagnostics
    # ------------------------------------------------------------------

    date_cols = [
        col for col in df.columns
        if any(x in col.lower() for x in ["date", "time"])
    ]

    for col in date_cols:
        print(f"\n=== DATE DIAGNOSTICS: {col} ===")
        print(f"Non-null: {df[col].notna().sum():,}")
        print(f"Null: {df[col].isna().sum():,}")
        print("First 10 raw values:")
        print(df[col].head(10).map(repr).to_string(index=False))

        parsed = pd.to_datetime(df[col], errors="coerce")

        print(f"Successfully parsed: {parsed.notna().sum():,}")
        print(f"Failed parsing: {parsed.isna().sum():,}")

        if parsed.notna().any():
            print(f"Minimum date: {parsed.min()}")
            print(f"Maximum date: {parsed.max()}")
            print(f"Unique dates: {parsed.nunique()}")

    # ------------------------------------------------------------------
    # NDVI diagnostics
    # ------------------------------------------------------------------

    ndvi_cols = [
        col for col in df.columns
        if "ndvi" in col.lower()
        or "250m_16_days" in col.lower()
    ]

    for col in ndvi_cols:
        print(f"\n=== NDVI DIAGNOSTICS: {col} ===")

        numeric = pd.to_numeric(df[col], errors="coerce")

        print(f"Non-null raw values: {numeric.notna().sum():,}")
        print(f"Non-numeric/unparseable: {numeric.isna().sum():,}")

        if numeric.notna().any():
            print(f"Raw minimum: {numeric.min()}")
            print(f"Raw maximum: {numeric.max()}")
            print(f"Raw mean: {numeric.mean()}")
            print(f"Raw median: {numeric.median()}")

            print("\nMost common raw values:")
            print(numeric.value_counts(dropna=False).head(20).to_string())

            print("\nSentinel/fill candidates:")
            for candidate in [-3000, -2000, -9999, 0, 32767, 65535]:
                count = (numeric == candidate).sum()
                if count:
                    print(f"  {candidate}: {count:,}")

            print("\nValues outside expected scaled NDVI range [-1, 1]:")
            outside = numeric[(numeric < -1) | (numeric > 1)]
            print(f"Count: {len(outside):,}")

            if len(outside):
                print("Most common outside-range values:")
                print(outside.value_counts().head(20).to_string())

    # ------------------------------------------------------------------
    # Missingness
    # ------------------------------------------------------------------

    print("\n=== MISSINGNESS BY COLUMN ===")

    missing = df.isna().sum()
    missing_pct = (missing / len(df) * 100).round(2)

    missing_summary = pd.DataFrame({
        "missing": missing,
        "missing_pct": missing_pct,
    })

    print(missing_summary.to_string())

    # ------------------------------------------------------------------
    # Final structural checks
    # ------------------------------------------------------------------

    print("\n=== STRUCTURAL CHECKS ===")

    print(f"Expected AppEEARS points/cells: {EXPECTED_CELLS}")

    for col in possible_id_cols:
        print(
            f"{col}: {df[col].nunique(dropna=True)} unique non-null values"
        )

    print("\nDiagnostic complete.")
    print("NO FILES WERE MODIFIED.")


if __name__ == "__main__":
    main()
