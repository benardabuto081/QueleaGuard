"""
Milestone 3.9 (final) - Sample the final pseudo-absence set from the
candidate pool, targeting a 1:1 ratio with presence records (133), per
Log Entry 009's ratio guidance for tree-based ML models.

Output: data/processed/pseudo_absences_final.csv
        reports/milestone_3_9_final_sampling_summary.txt
"""

import pandas as pd

POOL_PATH = "data/processed/pseudo_absence_pool.csv"
OUTPUT_PATH = "data/processed/pseudo_absences_final.csv"
SUMMARY_PATH = "reports/milestone_3_9_final_sampling_summary.txt"
TARGET_COUNT = 133  # matches presence count, per Log Entry 009's 1:1 ratio guidance

RANDOM_SEED = 42  # fixed seed for reproducibility


def main():
    pool = pd.read_csv(POOL_PATH)
    print(f"Candidate pool size: {len(pool)}")
    print(f"Target pseudo-absence count: {TARGET_COUNT}")

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

    summary = f"""Milestone 3.9 - Final Pseudo-Absence Sample Summary
========================================================

Method: Approximate Target-Group Background sampling (Log Entry 009)
Candidate pool: {len(pool)} records across 104 grid cells
Target ratio: 1:1 with presence records (133 presences -> 133 pseudo-absences)
Final sample size: {len(sampled)}
Random seed: {RANDOM_SEED} (fixed for reproducibility)

Unique grid cells represented: {sampled['grid_cell_id'].nunique()}
Pseudo-absences within Ahero scheme boundary: {sampled['within_scheme_boundary'].sum()}
Pseudo-absences in surrounding buffer: {(~sampled['within_scheme_boundary']).sum()}
Year range: {sampled['year'].min():.0f} - {sampled['year'].max():.0f}

Each pseudo-absence carries a real observation date (from the other-species
record that generated it), satisfying the Log Entry 006 requirement that
every pseudo-absence be assignable to environmental features using the
same temporal logic as true presences.
"""
    with open(SUMMARY_PATH, "w") as f:
        f.write(summary)
    print(f"\nSaved summary to {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
