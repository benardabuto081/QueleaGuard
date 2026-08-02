"""
Milestone 3.4 (final) - Extract CHIRPS rainfall features (7/30/90-day
antecedent windows) for all 133 modelling-candidate records.

Architecture:
1. Grid cell centroids computed via projected CRS (UTM 36S -> WGS84).
2. Determine, for every unique date needed, exactly which grid cells
   require a value on that date (many records share dates/cells).
3. Open each unique daily raster exactly once (via GDAL /vsigzip/, no
   decompression to disk), extract all needed cell values for that date,
   then move to the next date. Each of the ~3,247 cached files is opened
   at most once total, regardless of how many records reference it.
4. Assemble per-record 7/30/90-day sums from the extracted values.

Output: data/processed/rainfall_features.csv
        reports/milestone_3_4_rainfall_extraction_summary.txt
"""

import time
from pathlib import Path
from datetime import timedelta
from collections import defaultdict

import pandas as pd
import geopandas as gpd
import rasterio

OCCURRENCES_PATH = "data/processed/occurrences_with_grid_cell.csv"
GRID_PATH = "data/processed/analysis_grid.geojson"
CACHE_DIR = Path("data/external/chirps_cache")
OUTPUT_PATH = "data/processed/rainfall_features.csv"
SUMMARY_PATH = "reports/milestone_3_4_rainfall_extraction_summary.txt"
UTM_CRS = "EPSG:32736"
WGS84_CRS = "EPSG:4326"


def load_candidates_and_centroids():
    occ = pd.read_csv(OCCURRENCES_PATH)
    occ["year"] = pd.to_numeric(occ["year"], errors="coerce")
    candidates = occ[(occ["year"] >= 2000) & (occ["grid_cell_id"].notna())].copy()
    candidates["eventDate_clean"] = candidates["eventDate"].str[:10]
    candidates["eventDate_parsed"] = pd.to_datetime(
        candidates["eventDate_clean"], format="%Y-%m-%d", errors="coerce"
    )
    candidates = candidates.dropna(subset=["eventDate_parsed"])

    grid = gpd.read_file(GRID_PATH)
    grid_utm = grid.to_crs(UTM_CRS)
    centroids_utm = grid_utm.geometry.centroid
    centroids_gdf = gpd.GeoDataFrame(
        {"grid_cell_id": grid["grid_cell_id"]}, geometry=centroids_utm, crs=UTM_CRS
    ).to_crs(WGS84_CRS)
    centroids_gdf["centroid_lat"] = centroids_gdf.geometry.y
    centroids_gdf["centroid_lon"] = centroids_gdf.geometry.x
    centroids = centroids_gdf.set_index("grid_cell_id")[["centroid_lat", "centroid_lon"]]

    return candidates, centroids


def read_value(vsi_path, lat, lon):
    with rasterio.open(vsi_path) as src:
        row, col = src.index(lon, lat)
        value = src.read(1)[row, col].item()
        return max(value, 0.0)  # clamp CHIRPS no-data sentinel to 0


def main():
    candidates, centroids = load_candidates_and_centroids()
    print(f"Modelling-candidate records: {len(candidates)}")

    # Step 1: build a date -> set of (cell_id, lat, lon) needed on that date
    date_to_cells = defaultdict(set)
    for _, row in candidates.iterrows():
        cell_id = row["grid_cell_id"]
        if cell_id not in centroids.index:
            continue
        lat = centroids.loc[cell_id, "centroid_lat"]
        lon = centroids.loc[cell_id, "centroid_lon"]
        obs_date = row["eventDate_parsed"]
        for days_back in range(91):
            d = (obs_date - timedelta(days=days_back)).date()
            date_to_cells[d].add((cell_id, lat, lon))

    total_dates = len(date_to_cells)
    print(f"Unique dates to process: {total_dates}")
    print(f"Total (date, cell) extractions needed: {sum(len(v) for v in date_to_cells.values())}")

    # Step 2: for each date, open the file once, extract all needed cell values
    values = {}  # (date, cell_id) -> rainfall value
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

        if i % 200 == 0 or i == total_dates:
            elapsed = time.time() - start_time
            rate = i / elapsed if elapsed > 0 else 0
            remaining = (total_dates - i) / rate if rate > 0 else 0
            print(f"[{i}/{total_dates}] dates processed | elapsed: {elapsed:.0f}s | "
                  f"est. remaining: {remaining:.0f}s | missing so far: {len(missing_files)}")

    print(f"\nAll daily rasters processed in {time.time() - start_time:.1f}s.")
    print(f"Missing files: {len(missing_files)}")

    # Step 3: assemble per-record 7/30/90-day sums from extracted values
    results = []
    for _, row in candidates.iterrows():
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
    print(f"\nExtracted rainfall features for {len(results_df)} of {len(candidates)} candidates.")
    print(f"Saved to {OUTPUT_PATH}")
    print("\nSample results:")
    print(results_df.head(10).to_string(index=False))

    summary = f"""Milestone 3.4 - CHIRPS Rainfall Feature Extraction Summary (final)
======================================================================

Candidate records: {len(candidates)}
Successfully extracted: {len(results_df)}
Unique dates processed: {total_dates}
Unique daily rasters opened: {total_dates - len(missing_files)} (each opened exactly once)
Missing files: {len(missing_files)}

Access method: local CHIRPS raster cache, read directly via GDAL's
/vsigzip/ virtual filesystem (confirmed working via smoke test) - no
decompression to disk at any point.

Grid cell centroids computed via projected CRS (EPSG:32736, UTM 36S),
reprojected to WGS84.

Windows computed: 7-day, 30-day, 90-day antecedent rainfall totals ending
on each record's observation date, per Log Entry 006.

Rainfall statistics across all records:
{results_df[['rainfall_7d', 'rainfall_30d', 'rainfall_90d']].describe().to_string()}
"""
    with open(SUMMARY_PATH, "w") as f:
        f.write(summary)
    print(f"\nSaved summary to {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
