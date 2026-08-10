"""
Milestone 3.9 (NDVI scope check) - Determine whether cell_0176 (and any
other scheme-boundary or grid cell) represents a genuine NDVI feature
gap in the modelling dataset, or simply wasn't requested because no
occurrence record ever needed it.

The modelling dataset's NDVI requirement is per-RECORD (each presence/
pseudo-absence needs a nearest-composite NDVI value for its own cell),
not per-grid-cell-in-general. This checks exactly which cells actual
modelling records (presences + pseudo-absences) fall into, and whether
each has NDVI coverage.
"""

import pandas as pd

presences = pd.read_csv("data/processed/occurrences_with_grid_cell.csv")
presences["year"] = pd.to_numeric(presences["year"], errors="coerce")
presence_candidates = presences[(presences["year"] >= 2000) & (presences["grid_cell_id"].notna())]

pseudo_absences = pd.read_csv("data/processed/pseudo_absences_final.csv")

all_modelling_cells = set(presence_candidates["grid_cell_id"]) | set(pseudo_absences["grid_cell_id"])
print(f"Total unique grid cells actually used by modelling records (presences + pseudo-absences): {len(all_modelling_cells)}")

ndvi_history = pd.read_csv("data/external/appeears_ndvi_full_history.csv")
ndvi_covered_cells = set(ndvi_history["ID"].unique())
print(f"Grid cells with NDVI time series requested/available: {len(ndvi_covered_cells)}")

missing_ndvi = all_modelling_cells - ndvi_covered_cells
print(f"\nModelling-relevant cells WITHOUT NDVI coverage: {missing_ndvi if missing_ndvi else 'NONE - full coverage confirmed'}")

if missing_ndvi:
    # Check whether these gaps come from presence or pseudo-absence records
    affected_presence_records = presence_candidates[presence_candidates["grid_cell_id"].isin(missing_ndvi)]
    affected_pa_records = pseudo_absences[pseudo_absences["grid_cell_id"].isin(missing_ndvi)]
    print(f"\nAffected presence records: {len(affected_presence_records)}")
    print(f"Affected pseudo-absence records: {len(affected_pa_records)}")
else:
    print("\nEvery grid cell referenced by an actual modelling record (presence or pseudo-absence) has NDVI coverage.")
    print("cell_0176 was correctly excluded from the original NDVI request because no modelling")
    print("record (presence or pseudo-absence) falls in it - not a feature gap in the final dataset.")
