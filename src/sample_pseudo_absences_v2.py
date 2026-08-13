"""
Milestone 4.4 (correction, final) - Sample the final pseudo-absence set
from the corrected, presence-conflict-safe, month-stratified candidate
pool. Same 1:1 target ratio and fixed seed as the original (Log Entry 009),
applied to the corrected pool.

Backs up the v1 (month-biased) final sample before overwriting.

Output: data/processed/pseudo_absences_final.csv (rebuilt)
        data/processed/pseudo_absences_final_v1_month_skewed.csv (backup)
"""

import os
import shutil
import pandas as pd

POOL_PATH = "data/processed/pseudo_absence_pool.csv"
OUTPUT_PATH = "data/processed/pseudo_absences_final.csv"
BACKUP_PATH = "data/processed/pseudo_absences_final_v1_month_skewed.csv"
SUMMARY_PATH = "reports/milestone_4_4_final_sampling_v2_summary.txt"
TARGET_COUNT = 133
RANDOM_SEED = 42


def main():
    if os.path.exists(OUTPUT_PATH) and not os.path.exists(BACKUP_PATH):
        shutil.copy(OUTPUT_PATH, BACKUP_PATH)
        print(f"Backed up v1 final sample to {BACKUP_PATH}")

    pool = pd.read_csv(POOL_PATH)
    print(f"Candidate pool size: {len(pool)}")

    sample_size = min(TARGET_COUNT, len(pool))
    sampled = pool.sample(n=sample_size, random_state=RANDOM_SEED).reset_index(drop=True)

    sampled["record_type"] = "pseudo_absence"
    sampled["presence"] = 0

    sampled.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSampled {len(sampled)} pseudo-absences.")
    print(f"Saved to {OUTPUT_PATH}")

    print(f"\nUnique grid cells in final sample: {sampled['grid_cell_id'].nunique()}")
    print(f"Within-scheme-boundary pseudo-absences: {sampled['within_scheme_boundary'].sum()}")
    print(f"Year range: {sampled['year'].min():.0f} - {sampled['year'].max():.0f}")

    sampled["_month"] = pd.to_datetime(sampled["eventDate"], errors="coerce").dt.month
    print(f"\nMonth distribution in final sample:")
    print(sampled["_month"].value_counts().sort_index())

    summary = f"""Milestone 4.4 - Corrected Final Pseudo-Absence Sample
===========================================================

Method: Approximate Target-Group Background sampling (Log Entry 009),
rebuilt on a month-stratified, presence-conflict-safe effort pool
(Log Entry 014, pending).

Candidate pool: {len(pool)} records across {pool['grid_cell_id'].nunique()} grid cells
Target ratio: 1:1 with presence records
Final sample size: {len(sampled)}
Random seed: {RANDOM_SEED} (fixed for reproducibility)

Unique grid cells represented: {sampled['grid_cell_id'].nunique()}
Pseudo-absences within Ahero scheme boundary: {sampled['within_scheme_boundary'].sum()}
Year range: {sampled['year'].min():.0f} - {sampled['year'].max():.0f}

v1 (month-biased) sample backed up to: {BACKUP_PATH}
"""
    with open(SUMMARY_PATH, "w") as f:
        f.write(summary)
    print(f"\nSaved summary to {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
