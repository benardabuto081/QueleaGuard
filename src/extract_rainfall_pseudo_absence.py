"""
Milestone 3.10 (gap fix) - Extract CHIRPS rainfall features for the 133
pseudo-absence records, using the same date-batched /vsigzip/ approach
as Milestone 3.4 (presence records). Reuses the existing local CHIRPS
cache - no new downloads needed unless new dates are required.

Output: data/processed/rainfall_features_pseudo_absence.csv
"""

import time
from pathlib import Path
from datetime import timedelta
from collections import defaultdict

import pandas as pd
import geopandas as gpd
import rasterio

PSEUDO_ABSENCES_PATH = "data/processed/pseudo_absences_final.csv"
GRID_PATH = "data/processed/analysis_grid.geojson"
CACHE_DIR = Path("data/external/chirps_cache")
OUTPUT_PATH = "data/processed/rainfall_features_pseudo_absence.csv"
UTM_CRS = "EPSG:32736"
WGS84_CRS = "EPSG:4326"


def main():
    pa = pd.read_csv(PSEUDO_ABSENCES_PATH)
    pa["eventDate_parsed"] = pd.to_datetime(pa["eventDate"].astype(str).str[:10], format="%Y-%m-%d", errors="coerce")
    pa = pa.dropna(subset=["eventDate_parsed"])
    print(f"Pseudo-absence records: {len(pa)}")

    grid = gpd.read_file(GRID_PATH)
    grid_utm = grid.to_crs(UTM_CRS)
    centroids_utm = grid_utm.geometry.centroid
    centroids_gdf = gpd.GeoDataFrame(
        {"grid_cell_id": grid["grid_cell_id"]}, geometry=centroids_utm, crs=UTM_CRS
    ).to_crs(WGS84_CRS)
    centroids_gdf["centroid_lat"] = centroids_gdf.geometry.y
    centroids_gdf["centroid_lon"] = centroids_gdf.geometry.x
    centroids = centroids_gdf.set_index("grid_cell_id")[["centroid_lat", "centroid_lon"]]

    date_to_cells = defaultdict(set)
    for _, row in pa.iterrows():
        cell_id = row["grid_cell_id"]
        if cell_id not in centroids.index:
            continue
        lat, lon = centroids.loc[cell_id, "centroid_lat"], centroids.loc[cell_id, "centroid_lon"]
        obs_date = row["eventDate_parsed"]
        for days_back in range(91):
            d = (obs_date - timedelta(days=days_back)).date()
            date_to_cells[d].add((cell_id, lat, lon))

    total_dates = len(date_to_cells)
    print(f"Unique dates needed: {total_dates}")

    values = {}
    missing_files = []
    start_time = time.time()

    for i, (date_obj, cells) in enumerate(sorted(date_to_cells.items()), 1):
        gz_path = CACHE_DIR / str(date_obj.year) / f"chirps-v2.0.{date_obj:%Y.%m.%d}.tif.gz"
        vsi_path = f"/vsigzip/{gz_path.resolve().as_posix()}"

        if not gz_path.exists():
            missing_files.append(str(gz_path))
            continue

        with rasterio.open(vsi_path) as src:
            band = src.read(1)
            for cell_id, lat, lon in cells:
                row, col = src.index(lon, lat)
                val = max(band[row, col].item(), 0.0)
                values[(date_obj, cell_id)] = val

        if i % 100 == 0 or i == total_dates:
            elapsed = time.time() - start_time
            print(f"[{i}/{total_dates}] processed | elapsed: {elapsed:.0f}s | missing: {len(missing_files)}")

    print(f"\nDone in {time.time() - start_time:.1f}s. Missing files: {len(missing_files)}")
    if missing_files:
        print("NOTE: missing files will need downloading - see next step if this list is non-empty.")
        print(missing_files[:10])

    results = []
    for _, row in pa.iterrows():
        cell_id = row["grid_cell_id"]
        if cell_id not in centroids.index:
            continue
        obs_date = row["eventDate_parsed"]

        daily = {}
        for days_back in range(91):
            d = (obs_date - timedelta(days=days_back)).date()
            if (d, cell_id) in values:
                daily[d] = values[(d, cell_id)]

        rain_7d = sum(v for d, v in daily.items() if d > (obs_date - timedelta(days=7)).date())
        rain_30d = sum(v for d, v in daily.items() if d > (obs_date - timedelta(days=30)).date())
        rain_90d = sum(daily.values())

        results.append({
            "record_key": row["key"],
            "grid_cell_id": cell_id,
            "observation_date": obs_date.date(),
            "rainfall_7d": round(rain_7d, 2),
            "rainfall_30d": round(rain_30d, 2),
            "rainfall_90d": round(rain_90d, 2),
            "days_with_data": len(daily),
        })

    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nExtracted rainfall for {len(results_df)} pseudo-absence records.")
    print(f"Saved to {OUTPUT_PATH}")
    print(f"Records with incomplete data: {(results_df['days_with_data'] < 90).sum()}")


if __name__ == "__main__":
    main()
