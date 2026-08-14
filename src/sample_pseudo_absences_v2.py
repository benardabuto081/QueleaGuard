"""
Milestone 4.4 - Final pseudo-absence sampling.

Samples 1:1 pseudo-absences against the actual presence records used
in the modelling dataset.

Important:
- Presence count is NOT inferred from pseudo_absence_pool.csv.
- Presence records are loaded from occurrences_with_grid_cell.csv.
- Candidate dates/months come from pseudo_absence_pool.csv.
- Sampling is month-stratified according to the actual presence-month
  distribution.
- Fixed random seed for reproducibility.
- Existing v1 output is preserved as a backup.
"""

import os
import shutil
import pandas as pd

PRESENCE_PATH = "data/processed/occurrences_with_grid_cell.csv"
POOL_PATH = "data/processed/pseudo_absence_pool.csv"

OUTPUT_PATH = "data/processed/pseudo_absences_final.csv"
BACKUP_PATH = "data/processed/pseudo_absences_final_v1_month_skewed.csv"
SUMMARY_PATH = "reports/milestone_4_4_final_sampling_v2_summary.txt"

RANDOM_SEED = 42
EXPECTED_PRESENCE_COUNT = 133


def get_month(series):
    """
    Extract month robustly from eventDate.
    Falls back to an existing month column if available.
    """
    dates = pd.to_datetime(series, errors="coerce")
    return dates.dt.month


def main():

    # ------------------------------------------------------------
    # 1. BACK UP EXISTING FINAL SAMPLE
    # ------------------------------------------------------------

    if os.path.exists(OUTPUT_PATH) and not os.path.exists(BACKUP_PATH):
        shutil.copy2(OUTPUT_PATH, BACKUP_PATH)
        print(f"Backed up previous final sample to:\n  {BACKUP_PATH}")
    else:
        print("Backup already exists or previous output does not exist.")

    # ------------------------------------------------------------
    # 2. LOAD PRESENCE DATA
    # ------------------------------------------------------------

    presence = pd.read_csv(PRESENCE_PATH)

    print(f"\nPresence source: {PRESENCE_PATH}")
    print(f"Presence records loaded: {len(presence)}")

    # Use eventDate as the authoritative temporal field.
    presence["_month"] = get_month(presence["eventDate"])

    valid_presence = presence.dropna(subset=["_month"]).copy()
    valid_presence["_month"] = valid_presence["_month"].astype(int)

    print(f"Presence records with valid dates: {len(valid_presence)}")

    if len(valid_presence) == 0:
        raise RuntimeError(
            "No presence records with valid eventDate values were found."
        )

    if len(valid_presence) != EXPECTED_PRESENCE_COUNT:
        print(
            f"\nWARNING: Expected approximately "
            f"{EXPECTED_PRESENCE_COUNT} presence records, "
            f"but found {len(valid_presence)}."
        )

    TARGET_COUNT = len(valid_presence)

    # ------------------------------------------------------------
    # 3. LOAD CANDIDATE POOL
    # ------------------------------------------------------------

    pool = pd.read_csv(POOL_PATH)

    print(f"\nCandidate pool size: {len(pool)}")

    pool["_month"] = get_month(pool["eventDate"])

    pool = pool.dropna(subset=["_month"]).copy()
    pool["_month"] = pool["_month"].astype(int)

    print(f"Candidate records with valid dates: {len(pool)}")

    # Remove duplicate GBIF keys before sampling.
    if "key" in pool.columns:
        before = len(pool)
        pool = pool.drop_duplicates(subset=["key"])
        removed = before - len(pool)

        if removed:
            print(f"Removed duplicate candidate GBIF keys: {removed}")

    # ------------------------------------------------------------
    # 4. REMOVE ANY CANDIDATES THAT ARE PRESENCES
    # ------------------------------------------------------------

    if "key" in presence.columns and "key" in pool.columns:

        presence_keys = set(
            presence["key"]
            .dropna()
            .astype(str)
        )

        before = len(pool)

        pool = pool[
            ~pool["key"]
            .astype(str)
            .isin(presence_keys)
        ].copy()

        removed = before - len(pool)

        print(
            f"Presence-conflicting candidate records removed: {removed}"
        )

    # ------------------------------------------------------------
    # 5. PRESENCE MONTH DISTRIBUTION
    # ------------------------------------------------------------

    presence_months = (
        valid_presence["_month"]
        .value_counts()
        .sort_index()
    )

    print("\n=== PRESENCE MONTH DISTRIBUTION ===")
    print(presence_months)

    # ------------------------------------------------------------
    # 6. CANDIDATE MONTH DISTRIBUTION
    # ------------------------------------------------------------

    candidate_months = (
        pool["_month"]
        .value_counts()
        .sort_index()
    )

    print("\n=== CANDIDATE POOL MONTH DISTRIBUTION ===")
    print(candidate_months)

    # ------------------------------------------------------------
    # 7. MONTH-STRATIFIED SAMPLING
    # ------------------------------------------------------------

    # We want the pseudo-absence sample to follow the same month
    # distribution as the presence records.

    target_by_month = presence_months.to_dict()

    print("\n=== TARGET PSEUDO-ABSENCE MONTH DISTRIBUTION ===")

    for month in range(1, 13):
        print(
            f"Month {month:2d}: "
            f"{target_by_month.get(month, 0)}"
        )

    sampled_parts = []

    for month in range(1, 13):

        target = target_by_month.get(month, 0)

        if target == 0:
            continue

        candidates = pool[
            pool["_month"] == month
        ].copy()

        if len(candidates) < target:

            raise RuntimeError(
                f"Insufficient candidate records for month {month}.\n"
                f"Required: {target}\n"
                f"Available: {len(candidates)}\n\n"
                f"The corrected effort pool must contain enough "
                f"records in every month represented by the presence data."
            )

        sampled_month = candidates.sample(
            n=target,
            random_state=RANDOM_SEED + month
        )

        sampled_parts.append(sampled_month)

    # ------------------------------------------------------------
    # 8. COMBINE SAMPLE
    # ------------------------------------------------------------

    if not sampled_parts:
        raise RuntimeError(
            "No pseudo-absence records were sampled."
        )

    sampled = (
        pd.concat(sampled_parts, ignore_index=True)
        .sample(frac=1, random_state=RANDOM_SEED)
        .reset_index(drop=True)
    )

    # ------------------------------------------------------------
    # 9. FINAL METADATA
    # ------------------------------------------------------------

    sampled["record_type"] = "pseudo_absence"
    sampled["presence"] = 0

    # Remove internal helper column.
    sampled = sampled.drop(columns=["_month"], errors="ignore")

    # ------------------------------------------------------------
    # 10. FINAL VALIDATION
    # ------------------------------------------------------------

    final_month = get_month(sampled["eventDate"])

    print("\n=== FINAL VALIDATION ===")

    print(f"Final sample size: {len(sampled)}")

    if len(sampled) != TARGET_COUNT:
        raise RuntimeError(
            f"Final sample size mismatch. "
            f"Expected {TARGET_COUNT}, got {len(sampled)}."
        )

    if "grid_cell_id" in sampled.columns:
        print(
            f"Unique grid cells: "
            f"{sampled['grid_cell_id'].nunique()}"
        )

    if "within_scheme_boundary" in sampled.columns:
        print(
            "Within-scheme-boundary pseudo-absences: "
            f"{sampled['within_scheme_boundary'].sum()}"
        )

    if "year" in sampled.columns:
        years = pd.to_numeric(
            sampled["year"],
            errors="coerce"
        )

        print(
            f"Year range: "
            f"{int(years.min())} - {int(years.max())}"
        )

    print("\n=== FINAL MONTH DISTRIBUTION ===")

    print(
        final_month
        .value_counts()
        .sort_index()
    )

    # ------------------------------------------------------------
    # 11. DUPLICATE VALIDATION
    # ------------------------------------------------------------

    duplicate_keys = 0

    if "key" in sampled.columns:
        duplicate_keys = (
            sampled["key"]
            .duplicated()
            .sum()
        )

    print(f"\nDuplicate GBIF keys: {duplicate_keys}")

    if duplicate_keys > 0:
        raise RuntimeError(
            "Duplicate GBIF keys detected in final pseudo-absence sample."
        )

    # ------------------------------------------------------------
    # 12. SAVE
    # ------------------------------------------------------------

    sampled.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print(
        "\nSaved corrected final sample to:\n"
        f"  {OUTPUT_PATH}"
    )

    # ------------------------------------------------------------
    # 13. WRITE VALIDATION REPORT
    # ------------------------------------------------------------

    unique_cells = (
        sampled["grid_cell_id"].nunique()
        if "grid_cell_id" in sampled.columns
        else "N/A"
    )

    within_boundary = (
        sampled["within_scheme_boundary"].sum()
        if "within_scheme_boundary" in sampled.columns
        else "N/A"
    )

    years = pd.to_numeric(
        sampled["year"],
        errors="coerce"
    ) if "year" in sampled.columns else pd.Series(dtype=float)

    year_min = (
        int(years.min())
        if len(years) and not years.isna().all()
        else "N/A"
    )

    year_max = (
        int(years.max())
        if len(years) and not years.isna().all()
        else "N/A"
    )

    report = f"""
Milestone 4.4 - Corrected Final Pseudo-Absence Sampling
========================================================

Method:
Month-stratified target-group background sampling.

Presence source:
{PRESENCE_PATH}

Candidate pool:
{POOL_PATH}

Presence records with valid dates:
{len(valid_presence)}

Target pseudo-absence count:
{TARGET_COUNT}

Final pseudo-absence count:
{len(sampled)}

Random seed:
{RANDOM_SEED}

Unique grid cells:
{unique_cells}

Within-scheme-boundary pseudo-absences:
{within_boundary}

Year range:
{year_min} - {year_max}

Duplicate GBIF keys:
{duplicate_keys}

Presence month distribution:
{presence_months.to_dict()}

Final pseudo-absence month distribution:
{final_month.value_counts().sort_index().to_dict()}

Previous v1 sample backup:
{BACKUP_PATH}
"""

    with open(
        SUMMARY_PATH,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(report.strip() + "\n")

    print(
        "\nSaved validation summary to:\n"
        f"  {SUMMARY_PATH}"
    )


if __name__ == "__main__":
    main()
