"""
Milestone 3.11 (fix) - Remove pseudo-absence records that share a
(grid_cell_id, observation_date) pair with a confirmed presence record.
This violates the Target-Group Background assumption: a pseudo-absence
represents "observer present, target species not detected," which cannot
hold true for a checklist/date/location where the target species WAS
confirmed present. Discovered during Milestone 3.11 validation
(cell_0079, 2016-01-17: 1 presence + 3 same-checklist pseudo-absences,
sequential GBIF keys 1710847627-1710848647).

Output: data/processed/modelling_dataset_final.csv (corrected)
        reports/milestone_3_11_final_assembly_summary.txt
"""

import pandas as pd

DATASET_PATH = "data/processed/modelling_dataset_final.csv"
OUTPUT_PATH = "data/processed/modelling_dataset_final.csv"
SUMMARY_PATH = "reports/milestone_3_11_final_assembly_summary.txt"


def main():
    df = pd.read_csv(DATASET_PATH)
    pre_count = len(df)

    # Find (cell, date) pairs with both presence and pseudo-absence records
    cross = df.groupby(["grid_cell_id", "observation_date"])["presence"].nunique()
    conflict_pairs = cross[cross > 1].index

    to_drop = df[
        df.set_index(["grid_cell_id", "observation_date"]).index.isin(conflict_pairs)
        & (df["record_type"] == "pseudo_absence")
    ]

    print(f"Conflicting (cell, date) pairs found: {len(conflict_pairs)}")
    print(f"Pseudo-absence records to drop (same checklist/date/cell as a confirmed presence):")
    print(to_drop[["record_key", "grid_cell_id", "observation_date", "record_type"]].to_string(index=False))

    df_corrected = df[~df["record_key"].isin(to_drop["record_key"])].copy()

    df_corrected.to_csv(OUTPUT_PATH, index=False)
    print(f"\nFinal modelling dataset: {len(df_corrected)} records ({pre_count} -> {len(df_corrected)})")
    print(f"\nClass balance:")
    print(df_corrected["presence"].value_counts())

    missing = df_corrected.isna().sum()
    summary = f"""Milestone 3.11 - Final Modelling Dataset (TGB contradiction fix)
==============================================================

Total records: {len(df_corrected)}
Presence: {(df_corrected['presence']==1).sum()}
Pseudo-absence: {(df_corrected['presence']==0).sum()}
Columns: {len(df_corrected.columns)}

Correction applied: 3 pseudo-absence records excluded because they shared
a (grid_cell_id, observation_date) pair with a confirmed Quelea quelea
presence record - all 4 records bear sequential GBIF keys consistent with
a single shared eBird checklist (cell_0079, 2016-01-17). This violates
the Target-Group Background pseudo-absence assumption (an observer was
present and did NOT detect the target species) and required correction,
not just documentation, per Log Entry 013.

Missing values by column:
{missing[missing > 0].to_string() if missing.sum() > 0 else 'None'}

This dataset incorporates: spatial framework (Log Entry 002), temporal
framework (Log Entry 006), pseudo-absence methodology (Log Entry 009,
010), NDVI quality-filter fix (Task 190 / Log Entry 012), and the
presence/pseudo-absence checklist-contradiction fix (Log Entry 013).
"""
    with open(SUMMARY_PATH, "w") as f:
        f.write(summary)
    print(f"\nSaved summary to {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
