"""
Level 2 - AFCD stationarity cross-check (Feasibility Study Section 4;
tests whether Jiang et al. 2025's single 2023 rice-extent snapshot can be
validly paired with older occurrence records).

For each of the 180 qualifying records (observation_year <= 2022, AFCD's
coverage ceiling), extracts AFCD cropland % within a 500m buffer at:
  - the record own observation year
  - year 2022 (closest AFCD year to the Jiang et al. 2023 rice snapshot)

AFCD source: Lou et al. 2025, Zenodo DOI 10.5281/zenodo.14920706,
read remotely via GDAL /vsicurl/ (confirmed internally tiled 128x128,
efficient for windowed reads - no full-file download required).

Output: data/processed/afcd_stationarity_check.csv
"""

import math
import os
import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import from_bounds

os.environ["GDAL_DISABLE_READDIR_ON_OPEN"] = "EMPTY_DIR"
os.environ["CPL_VSIL_CURL_USE_HEAD"] = "NO"
os.environ["GDAL_HTTP_MAX_RETRY"] = "3"
os.environ["GDAL_HTTP_RETRY_DELAY"] = "2"

AFCD_URL_TEMPLATE = "/vsicurl/https://zenodo.org/records/14920706/files/AFCD_{year}.tif?download=1"
INPUT_PATH = "data/processed/modelling_dataset_final.csv"
OUTPUT_PATH = "data/processed/afcd_stationarity_check.csv"

ANCHOR_YEAR = 2022
BUFFER_RADIUS_M = 500
M_PER_DEG_LAT = 111320.0


def deg_window(lat, lon, radius_m):
    dlat = radius_m / M_PER_DEG_LAT
    dlon = radius_m / (M_PER_DEG_LAT * math.cos(math.radians(lat)))
    return lon - dlon, lat - dlat, lon + dlon, lat + dlat


def cropland_pct(src, lat, lon, radius_m):
    minx, miny, maxx, maxy = deg_window(lat, lon, radius_m)
    window = from_bounds(minx, miny, maxx, maxy, src.transform)
    data = src.read(1, window=window)
    if data.size == 0:
        return np.nan
    transform = src.window_transform(window)
    rows, cols = np.indices(data.shape)
    xs, ys = rasterio.transform.xy(transform, rows.ravel(), cols.ravel())
    xs = np.array(xs).reshape(data.shape)
    ys = np.array(ys).reshape(data.shape)
    dx = (xs - lon) * M_PER_DEG_LAT * math.cos(math.radians(lat))
    dy = (ys - lat) * M_PER_DEG_LAT
    dist = np.sqrt(dx ** 2 + dy ** 2)
    within = dist <= radius_m
    n = within.sum()
    return float((data[within] == 1).mean() * 100) if n > 0 else np.nan


def main():
    df = pd.read_csv(INPUT_PATH)
    df["obs_year"] = df["observation_date"].str[:4].astype(int)
    qualifying = df[df["obs_year"] <= ANCHOR_YEAR][["record_key", "record_type", "latitude", "longitude", "obs_year"]].copy()
    qualifying = qualifying.reset_index(drop=True)
    print(f"Qualifying records (obs_year <= {ANCHOR_YEAR}): {len(qualifying)}")

    qualifying["own_year_cropland_pct"] = np.nan
    qualifying["anchor_2022_cropland_pct"] = np.nan

    distinct_years = sorted(qualifying["obs_year"].unique())
    print(f"Distinct observation years to fetch: {distinct_years}")

    for year in distinct_years:
        url = AFCD_URL_TEMPLATE.format(year=year)
        print(f"Opening AFCD_{year}.tif remotely...")
        with rasterio.open(url) as src:
            subset = qualifying[qualifying["obs_year"] == year]
            for idx, row in subset.iterrows():
                qualifying.loc[idx, "own_year_cropland_pct"] = cropland_pct(src, row["latitude"], row["longitude"], BUFFER_RADIUS_M)
        print(f"  {len(subset)} point(s) done for year {year}")

    print(f"\nOpening AFCD_{ANCHOR_YEAR}.tif remotely (anchor pass, all {len(qualifying)} points)...")
    url = AFCD_URL_TEMPLATE.format(year=ANCHOR_YEAR)
    with rasterio.open(url) as src:
        for idx, row in qualifying.iterrows():
            qualifying.loc[idx, "anchor_2022_cropland_pct"] = cropland_pct(src, row["latitude"], row["longitude"], BUFFER_RADIUS_M)
            if (idx + 1) % 50 == 0:
                print(f"  ...processed {idx + 1}")

    qualifying["abs_diff"] = (qualifying["anchor_2022_cropland_pct"] - qualifying["own_year_cropland_pct"]).abs()
    qualifying.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved to {OUTPUT_PATH}")

    print("\nSummary (all qualifying records):")
    print(f"Mean |difference|: {qualifying['abs_diff'].mean():.2f} percentage points")
    print(f"Median |difference|: {qualifying['abs_diff'].median():.2f} percentage points")
    print(f"Correlation (own-year vs 2022): {qualifying['own_year_cropland_pct'].corr(qualifying['anchor_2022_cropland_pct']):.3f}")

    pre2015 = qualifying[qualifying["obs_year"] < 2015]
    print(f"\nPre-2015 subset (n={len(pre2015)}, highest-risk group):")
    print(f"  Mean |difference|: {pre2015['abs_diff'].mean():.2f} percentage points")
    print(f"  Correlation: {pre2015['own_year_cropland_pct'].corr(pre2015['anchor_2022_cropland_pct']):.3f}")


if __name__ == "__main__":
    main()
