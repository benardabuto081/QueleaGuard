"""
Diagnose which pseudo-absence records lost their NDVI value after the
quality-filter fix (Task 190), and why.
"""

import pandas as pd

ndvi_pa = pd.read_csv("data/processed/ndvi_features_pseudo_absence.csv")
missing = ndvi_pa[ndvi_pa["ndvi_nearest_composite"].isna()]

print(f"Missing records: {len(missing)}\n")
print(missing[["record_key", "grid_cell_id", "observation_date"]].to_string(index=False))

# Cross-check: does this cell have ANY good-quality composite at all,
# regardless of date, or none ever?
original = pd.read_csv("data/external/appeears_ndvi_full_history.csv")
gap_fill = pd.read_csv("data/external/appeears_ndvi_pseudo_absence_gap.csv")
ndvi_all = pd.concat([original, gap_fill], ignore_index=True)
ndvi_all["Date"] = pd.to_datetime(ndvi_all["Date"])

QUALITY_COL = "MOD13Q1_061__250m_16_days_VI_Quality_MODLAND_Description"
ndvi_good = ndvi_all[ndvi_all[QUALITY_COL] == "VI produced with good quality"]

print("\nPer affected cell - earliest good-quality composite date available:")
for cell_id in missing["grid_cell_id"].unique():
    cell_good = ndvi_good[ndvi_good["ID"] == cell_id].sort_values("Date")
    if cell_good.empty:
        print(f"  {cell_id}: NO good-quality composites exist at all")
    else:
        print(f"  {cell_id}: earliest good composite = {cell_good['Date'].min().date()}, "
              f"total good composites = {len(cell_good)}")
