"""
QueleaGuard - FINAL ENVIRONMENTAL DATA INTEGRITY AUDIT

Purpose:
    Audit the current environmental/modeling datasets before final NDVI
    completion and model training.

This is an audit only.
It does not modify project data.
"""

from pathlib import Path
import pandas as pd
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
EXTERNAL = ROOT / "data" / "external"
REPORTS = ROOT / "reports"

REPORTS.mkdir(exist_ok=True)


def load(name, folder=PROCESSED):
    path = folder / name
    if not path.exists():
        print(f"[MISSING] {path}")
        return None

    try:
        df = pd.read_csv(path)
        print(f"[LOADED] {name}: {len(df):,} rows x {len(df.columns)} columns")
        return df
    except Exception as e:
        print(f"[ERROR] {name}: {e}")
        return None


def section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def pct(n, d):
    return (100 * n / d) if d else 0.0


print("=" * 80)
print("QUELEAGUARD - FINAL ENVIRONMENTAL DATA INTEGRITY AUDIT")
print("=" * 80)
print(f"Project root: {ROOT}")


# ---------------------------------------------------------------------------
# LOAD CORE DATASETS
# ---------------------------------------------------------------------------

section("LOADING DATASETS")

occ = load("occurrences_with_grid_cell.csv")
pa = load("pseudo_absences_final.csv")
final = load("modelling_dataset_final.csv")
partial = load("modelling_dataset_partial.csv")

rain = load("rainfall_features.csv")
rain_pa = load("rainfall_features_pseudo_absence.csv")

met = load("meteorology_features.csv")
met_pa = load("meteorology_features_pseudo_absence.csv")

terrain = load("terrain_features.csv")
hydro = load("hydrology_features.csv")

ndvi = load("ndvi_features.csv")
ndvi_pa = load("ndvi_features_pseudo_absence.csv")

missing = load("ndvi_missing_cells_manifest.csv")


# ---------------------------------------------------------------------------
# DATASET COUNTS
# ---------------------------------------------------------------------------

section("1. DATASET COUNTS")

if occ is not None:
    print(f"Presence occurrence records:       {len(occ):,}")
    print(f"Presence unique record keys:       {occ['key'].nunique():,}")

if pa is not None:
    print(f"Pseudo-absence records:            {len(pa):,}")
    print(f"Pseudo-absence unique keys:        {pa['key'].nunique():,}")

if final is not None:
    print(f"Final modelling rows:              {len(final):,}")

if partial is not None:
    print(f"Partial modelling rows:            {len(partial):,}")


# ---------------------------------------------------------------------------
# RECORD TYPE BALANCE
# ---------------------------------------------------------------------------

section("2. PRESENCE / PSEUDO-ABSENCE BALANCE")

if final is not None and "record_type" in final.columns:
    counts = final["record_type"].value_counts(dropna=False)

    for label, count in counts.items():
        print(f"{str(label):25s}: {count:6,} ({pct(count, len(final)):6.2f}%)")

    if "presence" in final.columns:
        print("\nTarget distribution:")
        print(final["presence"].value_counts(dropna=False).to_string())


# ---------------------------------------------------------------------------
# DUPLICATES
# ---------------------------------------------------------------------------

section("3. DUPLICATE AUDIT")

for name, df, key in [
    ("occurrences", occ, "key"),
    ("pseudo_absences", pa, "key"),
    ("final_model", final, "record_key"),
]:

    if df is None or key not in df.columns:
        continue

    duplicate_rows = df.duplicated().sum()
    duplicate_keys = df[key].duplicated().sum()

    print(f"{name:20s} duplicate rows: {duplicate_rows:,}")
    print(f"{name:20s} duplicate {key}: {duplicate_keys:,}")


# ---------------------------------------------------------------------------
# GRID COVERAGE
# ---------------------------------------------------------------------------

section("4. SPATIAL / GRID COVERAGE")

for name, df, col in [
    ("occurrences", occ, "grid_cell_id"),
    ("pseudo_absences", pa, "grid_cell_id"),
    ("final_model", final, "grid_cell_id"),
]:

    if df is None or col not in df.columns:
        continue

    print(
        f"{name:20s} unique grid cells: "
        f"{df[col].nunique():,}"
    )

if final is not None and "within_scheme_boundary" in final.columns:
    print("\nFinal model boundary distribution:")
    print(
        final["within_scheme_boundary"]
        .value_counts(dropna=False)
        .to_string()
    )


# ---------------------------------------------------------------------------
# TEMPORAL COVERAGE
# ---------------------------------------------------------------------------

section("5. TEMPORAL COVERAGE")

for name, df, date_col in [
    ("occurrences", occ, "eventDate"),
    ("pseudo_absences", pa, "eventDate"),
    ("final_model", final, "observation_date"),
]:

    if df is None or date_col not in df.columns:
        continue

    dates = pd.to_datetime(df[date_col], errors="coerce")

    print(f"\n{name}")
    print(f"  Valid dates: {dates.notna().sum():,}/{len(df):,}")
    print(f"  Earliest:    {dates.min()}")
    print(f"  Latest:      {dates.max()}")


# ---------------------------------------------------------------------------
# MISSING VALUES
# ---------------------------------------------------------------------------

section("6. FINAL MODEL MISSINGNESS")

if final is not None:

    missing_counts = final.isna().sum()
    missing_counts = missing_counts[missing_counts > 0].sort_values(ascending=False)

    if len(missing_counts) == 0:
        print("[PASS] No missing values in final modelling dataset.")
    else:
        print("Columns containing missing values:")
        for col, count in missing_counts.items():
            print(
                f"{col:30s}: {count:6,} "
                f"({pct(count, len(final)):6.2f}%)"
            )


# ---------------------------------------------------------------------------
# ENVIRONMENTAL FEATURE COMPLETENESS
# ---------------------------------------------------------------------------

section("7. ENVIRONMENTAL FEATURE COMPLETENESS")

feature_groups = {
    "Rainfall": [
        "rainfall_7d",
        "rainfall_30d",
        "rainfall_90d",
    ],
    "Meteorology": [
        "temp_mean_7d",
        "dewpoint_mean_7d",
        "wind_mean_7d",
        "temp_same_day",
        "dewpoint_same_day",
        "wind_same_day",
    ],
    "NDVI": [
        "ndvi_nearest_composite",
        "ndvi_anomaly",
    ],
    "Terrain": [
        "elevation_m",
        "slope_deg",
    ],
    "Hydrology": [
        "dist_to_water_m",
    ],
}

if final is not None:

    for group, columns in feature_groups.items():

        existing = [c for c in columns if c in final.columns]

        if not existing:
            print(f"{group:15s}: [MISSING GROUP]")
            continue

        complete = final[existing].notna().all(axis=1).sum()

        print(
            f"{group:15s}: "
            f"{complete:,}/{len(final):,} rows complete "
            f"({pct(complete, len(final)):.2f}%)"
        )


# ---------------------------------------------------------------------------
# NDVI AUDIT
# ---------------------------------------------------------------------------

section("8. NDVI AUDIT")

if ndvi is not None:

    print(f"NDVI feature rows:       {len(ndvi):,}")
    print(f"Unique record keys:      {ndvi['record_key'].nunique():,}")

    if "ndvi_nearest_composite" in ndvi.columns:

        vals = pd.to_numeric(
            ndvi["ndvi_nearest_composite"],
            errors="coerce"
        )

        print("\nNDVI value range:")
        print(f"  Minimum: {vals.min()}")
        print(f"  Maximum: {vals.max()}")
        print(f"  Missing: {vals.isna().sum():,}")

        suspicious = ((vals < -1) | (vals > 1)).sum()

        print(
            f"  Outside [-1, 1]: {suspicious:,}"
        )

    if "ndvi_days_gap" in ndvi.columns:

        gaps = pd.to_numeric(
            ndvi["ndvi_days_gap"],
            errors="coerce"
        )

        print("\nTemporal alignment:")
        print(f"  Mean gap:   {gaps.mean():.2f} days")
        print(f"  Median gap: {gaps.median():.2f} days")
        print(f"  Maximum:    {gaps.max():.2f} days")


# ---------------------------------------------------------------------------
# NDVI MISSING CELLS
# ---------------------------------------------------------------------------

section("9. OUTSTANDING NDVI CELLS")

if missing is not None:

    print(
        f"Outstanding cells: "
        f"{len(missing):,}"
    )

    if "grid_cell_id" in missing.columns:
        print(
            missing["grid_cell_id"]
            .astype(str)
            .tolist()
        )


# ---------------------------------------------------------------------------
# PSEUDO-ABSENCE TEMPORAL COMPARISON
# ---------------------------------------------------------------------------

section("10. TEMPORAL COMPARABILITY")

if final is not None and "record_type" in final.columns:

    dates = pd.to_datetime(
        final["observation_date"],
        errors="coerce"
    )

    tmp = final.copy()
    tmp["_date"] = dates
    tmp["_year"] = dates.dt.year
    tmp["_month"] = dates.dt.month

    print("\nYear distribution:")
    print(
        pd.crosstab(
            tmp["_year"],
            tmp["record_type"]
        ).to_string()
    )

    print("\nMonth distribution:")
    print(
        pd.crosstab(
            tmp["_month"],
            tmp["record_type"]
        ).to_string()
    )


# ---------------------------------------------------------------------------
# SPATIAL CONCENTRATION
# ---------------------------------------------------------------------------

section("11. SPATIAL CONCENTRATION")

if final is not None:

    spatial_counts = (
        final.groupby(["record_type", "grid_cell_id"])
        .size()
        .reset_index(name="n")
    )

    for record_type in spatial_counts["record_type"].unique():

        subset = spatial_counts[
            spatial_counts["record_type"] == record_type
        ]

        print(f"\n{record_type}")

        print(
            f"  Cells represented: {len(subset):,}"
        )
        print(
            f"  Max records in one cell: "
            f"{subset['n'].max():,}"
        )
        print(
            f"  Median records/cell: "
            f"{subset['n'].median():.1f}"
        )

        print("  Top 10 cells:")

        print(
            subset
            .sort_values("n", ascending=False)
            .head(10)
            .to_string(index=False)
        )


# ---------------------------------------------------------------------------
# VALUE SANITY
# ---------------------------------------------------------------------------

section("12. VALUE SANITY CHECKS")

if final is not None:

    numeric_ranges = {
        "rainfall_7d": (0, None),
        "rainfall_30d": (0, None),
        "rainfall_90d": (0, None),
        "temp_mean_7d": (-20, 60),
        "dewpoint_mean_7d": (-20, 50),
        "wind_mean_7d": (0, 100),
        "ndvi_nearest_composite": (-1, 1),
        "ndvi_anomaly": (-2, 2),
        "elevation_m": (-100, 6000),
        "slope_deg": (0, 90),
        "dist_to_water_m": (0, None),
    }

    for col, (lo, hi) in numeric_ranges.items():

        if col not in final.columns:
            continue

        vals = pd.to_numeric(final[col], errors="coerce")

        bad = pd.Series(False, index=vals.index)

        if lo is not None:
            bad |= vals < lo

        if hi is not None:
            bad |= vals > hi

        print(
            f"{col:30s}: "
            f"{bad.sum():,} outside expected range"
        )


# ---------------------------------------------------------------------------
# FINAL READINESS
# ---------------------------------------------------------------------------

section("13. PRELIMINARY MODELING READINESS")

checks = {}

if final is not None:

    checks["final_dataset_exists"] = True
    checks["no_missing_values"] = final.isna().sum().sum() == 0

    checks["valid_target"] = (
        "presence" in final.columns
        and set(final["presence"].dropna().unique()).issubset({0, 1})
    )

    checks["has_presence"] = (
        "presence" in final.columns
        and (final["presence"] == 1).any()
    )

    checks["has_pseudo_absence"] = (
        "presence" in final.columns
        and (final["presence"] == 0).any()
    )

    checks["has_spatial_unit"] = (
        "grid_cell_id" in final.columns
    )

    checks["has_observation_date"] = (
        "observation_date" in final.columns
    )

    for name, value in checks.items():
        print(
            f"[{'PASS' if value else 'FAIL'}] "
            f"{name}"
        )

else:
    print("[FAIL] Final modelling dataset could not be loaded.")


# ---------------------------------------------------------------------------
# REPORT
# ---------------------------------------------------------------------------

report_path = REPORTS / "environmental_data_integrity_audit.txt"

with open(report_path, "w", encoding="utf-8") as f:

    f.write("QueleaGuard Environmental Data Integrity Audit\n")
    f.write("=" * 80 + "\n\n")

    if final is not None:

        f.write(f"Final modelling rows: {len(final):,}\n")

        if "record_type" in final.columns:
            f.write(
                "\nRecord type distribution:\n"
            )
            f.write(
                final["record_type"]
                .value_counts(dropna=False)
                .to_string()
            )
            f.write("\n")

        f.write("\nMissingness:\n")
        f.write(
            final.isna()
            .sum()
            .sort_values(ascending=False)
            .to_string()
        )

        f.write("\n\nSpatial cells:\n")
        if "grid_cell_id" in final.columns:
            f.write(
                str(final["grid_cell_id"].nunique())
            )

    f.write("\n\nAudit completed.\n")


print("\n" + "=" * 80)
print("AUDIT COMPLETE")
print("=" * 80)
print(f"Report: {report_path}")

