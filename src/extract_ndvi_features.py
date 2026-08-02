"""
Milestone 3.6 (final) - Download MODIS NDVI results and compute per-record
features: nearest composite value + seasonal anomaly, per Log Entry 006.

Output: data/external/appeears_ndvi_full_history.csv (raw time series)
        data/processed/ndvi_features.csv (per-record features)
        reports/milestone_3_6_ndvi_extraction_summary.txt
"""

import getpass
import requests
import pandas as pd
from datetime import timedelta

APPEEARS_API = "https://appeears.earthdatacloud.nasa.gov/api"
TASK_ID = "28801afb-d2dc-4c7f-b999-72f567a455bf"
OCCURRENCES_PATH = "data/processed/occurrences_with_grid_cell.csv"
RAW_OUTPUT = "data/external/appeears_ndvi_full_history.csv"
FEATURES_OUTPUT = "data/processed/ndvi_features.csv"
SUMMARY_PATH = "reports/milestone_3_6_ndvi_extraction_summary.txt"

NDVI_COL = "MOD13Q1_061__250m_16_days_NDVI"
QUALITY_COL = "MOD13Q1_061__250m_16_days_VI_Quality_MODLAND_Description"


def login():
    username = input("Earthdata username: ")
    password = getpass.getpass("Earthdata password (hidden as you type): ")
    response = requests.post(f"{APPEEARS_API}/login", auth=(username, password), timeout=30)
    response.raise_for_status()
    return response.json()["token"]


def main():
    token = login()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(f"{APPEEARS_API}/bundle/{TASK_ID}", headers=headers, timeout=30)
    response.raise_for_status()
    files = response.json()["files"]
    csv_file = next(f for f in files if f["file_name"].endswith("-results.csv"))
    file_id = csv_file["file_id"]

    print(f"Downloading: {csv_file['file_name']}")
    download_response = requests.get(f"{APPEEARS_API}/bundle/{TASK_ID}/{file_id}", headers=headers, timeout=120)
    download_response.raise_for_status()
    with open(RAW_OUTPUT, "wb") as f:
        f.write(download_response.content)
    print(f"Saved raw time series to {RAW_OUTPUT}")

    ndvi_df = pd.read_csv(RAW_OUTPUT)
    print(f"Raw time series rows: {len(ndvi_df)}")
    ndvi_df["Date"] = pd.to_datetime(ndvi_df["Date"])

    # Keep only good-quality observations for baseline/anomaly purposes
    good_quality = ndvi_df[ndvi_df[QUALITY_COL] == "VI produced with good quality"].copy()
    print(f"Good-quality rows: {len(good_quality)} of {len(ndvi_df)}")
    good_quality["month"] = good_quality["Date"].dt.month

    # Per-cell, per-month climatological mean NDVI (the seasonal baseline)
    seasonal_baseline = good_quality.groupby(["ID", "month"])[NDVI_COL].mean()

    occ = pd.read_csv(OCCURRENCES_PATH)
    occ["year"] = pd.to_numeric(occ["year"], errors="coerce")
    candidates = occ[(occ["year"] >= 2000) & (occ["grid_cell_id"].notna())].copy()
    candidates["eventDate_clean"] = candidates["eventDate"].str[:10]
    candidates["eventDate_parsed"] = pd.to_datetime(candidates["eventDate_clean"], format="%Y-%m-%d", errors="coerce")
    candidates = candidates.dropna(subset=["eventDate_parsed"])

    results = []
    for _, row in candidates.iterrows():
        cell_id = row["grid_cell_id"]
        obs_date = row["eventDate_parsed"]

        cell_series = ndvi_df[ndvi_df["ID"] == cell_id].sort_values("Date")
        prior = cell_series[cell_series["Date"] <= obs_date]

        if prior.empty:
            nearest_ndvi = None
            nearest_date = None
            days_gap = None
        else:
            nearest_row = prior.iloc[-1]
            nearest_ndvi = nearest_row[NDVI_COL]
            nearest_date = nearest_row["Date"]
            days_gap = (obs_date - nearest_date).days

        month = obs_date.month
        baseline = seasonal_baseline.get((cell_id, month), None)
        anomaly = (nearest_ndvi - baseline) if (nearest_ndvi is not None and baseline is not None) else None

        results.append({
            "record_key": row["key"],
            "grid_cell_id": cell_id,
            "observation_date": obs_date.date(),
            "ndvi_nearest_composite": round(nearest_ndvi, 4) if nearest_ndvi is not None else None,
            "ndvi_composite_date": nearest_date.date() if nearest_date is not None else None,
            "ndvi_days_gap": days_gap,
            "ndvi_seasonal_baseline": round(baseline, 4) if baseline is not None else None,
            "ndvi_anomaly": round(anomaly, 4) if anomaly is not None else None,
        })

    results_df = pd.DataFrame(results)
    results_df.to_csv(FEATURES_OUTPUT, index=False)
    print(f"\nExtracted NDVI features for {len(results_df)} records.")
    print(f"Saved to {FEATURES_OUTPUT}")
    print("\nSample results:")
    print(results_df.head(10).to_string(index=False))

    large_gaps = results_df[results_df["ndvi_days_gap"] > 16]
    summary = f"""Milestone 3.6 - MODIS NDVI Feature Extraction Summary
==========================================================

Candidate records: {len(candidates)}
Successfully extracted: {len(results_df)}
Records with composite gap > 16 days (i.e., relying on an older composite
than the typical 16-day cycle would suggest): {len(large_gaps)}

Access method: NASA AppEEARS point-extraction task, 20 unique grid cells,
full MODIS history (2000-2026) requested in a single task.

Nearest-composite logic: most recent 16-day NDVI composite at or before
each record's observation date, per Log Entry 006.

Seasonal anomaly: per-cell, per-calendar-month climatological mean NDVI
(good-quality observations only) subtracted from the nearest composite
value, capturing ecologically meaningful deviation from that location's
typical greenness for that time of year.

NDVI statistics across all records:
{results_df[['ndvi_nearest_composite', 'ndvi_anomaly']].describe().to_string()}
"""
    with open(SUMMARY_PATH, "w") as f:
        f.write(summary)
    print(f"\nSaved summary to {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
