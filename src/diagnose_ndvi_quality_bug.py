"""
Diagnostic - identify exactly which records have invalid NDVI values
(outside -1 to 1), and confirm the root cause: nearest-composite
selection not filtering by quality flag.
"""

import pandas as pd

df = pd.read_csv("data/processed/modelling_dataset_final.csv")
invalid = df[(df["ndvi_nearest_composite"] < -1) | (df["ndvi_nearest_composite"] > 1)]
print(f"Records with invalid NDVI: {len(invalid)} of {len(df)}")
print(invalid[["record_key", "grid_cell_id", "observation_date", "record_type", "ndvi_nearest_composite"]].to_string(index=False))

# Cross-check against raw NDVI history to confirm quality flag at that date
ndvi_history_presence = pd.read_csv("data/external/appeears_ndvi_full_history.csv")
ndvi_history_gap = pd.read_csv("data/external/appeears_ndvi_pseudo_absence_gap.csv")
ndvi_all = pd.concat([ndvi_history_presence, ndvi_history_gap], ignore_index=True)

QUALITY_COL = "MOD13Q1_061__250m_16_days_VI_Quality_MODLAND_Description"
for _, row in invalid.iterrows():
    matches = ndvi_all[(ndvi_all["ID"] == row["grid_cell_id"])]
    bad_quality = matches[matches["MOD13Q1_061__250m_16_days_NDVI"] < -1]
    print(f"\nCell {row['grid_cell_id']}: {len(bad_quality)} bad-quality composite(s) in its full history")
    if len(bad_quality) > 0:
        print(bad_quality[["Date", "MOD13Q1_061__250m_16_days_NDVI", QUALITY_COL]].head(3).to_string(index=False))
