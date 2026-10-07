import pandas as pd

df = pd.read_csv("data/processed/modelling_dataset_final.csv")

groups = {
    "Rainfall windows": ["rainfall_7d", "rainfall_30d", "rainfall_90d"],
    "Meteorology (mean vs same-day)": ["temp_mean_7d", "temp_same_day", "dewpoint_mean_7d", "dewpoint_same_day", "wind_mean_7d", "wind_same_day"],
    "NDVI": ["ndvi_nearest_composite", "ndvi_anomaly"],
    "Rice-density scales": ["rice_pct_500m", "rice_pct_1000m", "rice_pct_2000m", "dist_to_nearest_rice_m"],
    "Terrain/hydrology": ["elevation_m", "slope_deg", "dist_to_water_m"],
}

for name, cols in groups.items():
    print(f"=== {name} ===")
    print(df[cols].corr().round(2))
    print()
