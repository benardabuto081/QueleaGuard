"""
Milestone 3.4 - Extract CHIRPS rainfall (7/30/90-day antecedent windows)
for all feature-complete modelling candidate records, per the temporal
framework in Log Entry 006.

Uses NOAA's ERDDAP mirror of CHIRPS (griddap), which supports server-side
subsetting - each request returns only the small time/space slice needed,
avoiding full global raster downloads.

Rainfall is extracted at each record's grid cell centroid (the unit of
analysis, per Log Entry 002), not the raw occurrence coordinate.

Output: data/processed/rainfall_features.csv
        reports/milestone_3_4_rainfall_extraction_summary.txt
"""

import time
import requests
import pandas as pd
import geopandas as gpd
from datetime import datetime, timedelta

ERDDAP_BASE = "https://coastwatch.pfeg.noaa.gov/erddap/griddap/chirps20GlobalDailyP05.csv"

OCCURRENCES_PATH = "data/processed/occurrences_with_grid_cell.csv"
GRID_PATH = "data/processed/analysis_grid.geojson"
OUTPUT_PATH = "data/processed/rainfall_features.csv"
SUMMARY_PATH = "reports/milestone_3_4_rainfall_extraction_summary.txt"


def fetch_rainfall_series(lat, lon, end_date, days_back=90, retries=3):
    """Fetch daily rainfall at (lat, lon) for the `days_back` days ending on end_date."""
    start_date = end_date - timedelta(days=days_back)
    time_range = f"({start_date:%Y-%m-%d}T00:00:00Z):1:({end_date:%Y-%m-%d}T00:00:00Z)"
    url = (
        f"{ERDDAP_BASE}?precip[{time_range}][({lat}):1:({lat})][({lon}):1:({lon})]"
    )

    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            df = pd.read_csv(url, skiprows=[1])  # ERDDAP CSV has a units row to skip
            return df
        except Exception as e:
            if attempt == retries - 1:
                print(f"    Failed after {retries} attempts: {e}")
                return None
            time.sleep(3)
    return None


def main():
    occ = pd.read_csv(OCCURRENCES_PATH)
    occ["year"] = pd.to_numeric(occ["year"], errors="coerce")
    candidates = occ[(occ["year"] >= 2000) & (occ["grid_cell_id"].notna())].copy()
    print(f"Modelling-candidate records to process: {len(candidates)}")

    grid = gpd.read_file(GRID_PATH)
    grid["centroid_lat"] = grid.geometry.centroid.y
    grid["centroid_lon"] = grid.geometry.centroid.x
    centroids = grid.set_index("grid_cell_id")[["centroid_lat", "centroid_lon"]]

    results = []
    for i, row in candidates.iterrows():
        cell_id = row["grid_cell_id"]
        obs_date = pd.to_datetime(row["eventDate"], errors="coerce")
        if pd.isna(obs_date) or cell_id not in centroids.index:
            continue

        lat = centroids.loc[cell_id, "centroid_lat"]
        lon = centroids.loc[cell_id, "centroid_lon"]

        print(f"[{len(results)+1}/{len(candidates)}] {cell_id} @ {obs_date.date()}...")
        series = fetch_rainfall_series(lat, lon, obs_date, days_back=90)

        if series is None or "precip" not in series.columns:
            print("    No data retrieved, skipping.")
            continue

        series["time"] = pd.to_datetime(series["time"])
        series = series.sort_values("time")

        rain_7d = series[series["time"] > obs_date - timedelta(days=7)]["precip"].sum()
        rain_30d = series[series["time"] > obs_date - timedelta(days=30)]["precip"].sum()
        rain_90d = series["precip"].sum()

        results.append({
            "record_key": row["key"],
            "grid_cell_id": cell_id,
            "observation_date": obs_date.date(),
            "rainfall_7d": round(rain_7d, 2),
            "rainfall_30d": round(rain_30d, 2),
            "rainfall_90d": round(rain_90d, 2),
        })

        time.sleep(0.5)  # light courtesy delay between requests

    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nExtracted rainfall features for {len(results_df)} of {len(candidates)} candidates.")
    print(f"Saved to {OUTPUT_PATH}")

    summary = f"""Milestone 3.4 - CHIRPS Rainfall Feature Extraction Summary
==============================================================

Candidate records: {len(candidates)}
Successfully extracted: {len(results_df)}
Failed/skipped: {len(candidates) - len(results_df)}

Access method: NOAA ERDDAP griddap mirror of CHIRPS v2.0 daily
(server-side subsetting, no full global raster downloads)

Extraction unit: grid cell centroid (per Log Entry 002 unit of analysis),
not raw occurrence coordinate.

Windows computed: 7-day, 30-day, 90-day antecedent rainfall totals ending
on each record's observation date, per Log Entry 006.
"""
    with open(SUMMARY_PATH, "w") as f:
        f.write(summary)
    print(f"Saved summary to {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
