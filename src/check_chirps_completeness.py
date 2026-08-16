import pandas as pd
import os

pa = pd.read_csv("data/processed/pseudo_absences_final.csv")
pa["obs_date"] = pd.to_datetime(pa["eventDate"].astype(str).str[:10], format="%Y-%m-%d", errors="coerce")

missing_files = []
for _, row in pa.iterrows():
    if pd.isna(row["obs_date"]):
        continue
    for offset in range(90):
        d = row["obs_date"] - pd.Timedelta(days=offset)
        path = f"data/external/chirps_cache/{d.year}/chirps-v2.0.{d.year}.{d.month:02d}.{d.day:02d}.tif.gz"
        if not os.path.exists(path):
            missing_files.append(path)

missing_files = sorted(set(missing_files))
print(f"Missing CHIRPS files needed by pseudo-absence records: {len(missing_files)}")
if missing_files:
    print("Sample:", missing_files[:10])
