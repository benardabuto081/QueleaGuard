"""
Milestone 3.10 (meteorology gap fix) - Extract ERA5-Land meteorology
features for the 133 pseudo-absence records, following the same
7-day-window logic as Milestone 3.5 (presence records). Reuses the
existing month-cache where dates overlap; downloads only missing months.

Output: data/processed/meteorology_features_pseudo_absence.csv
"""

import time
import zipfile
from pathlib import Path
from datetime import timedelta
from collections import defaultdict

import cdsapi
import pandas as pd
import geopandas as gpd
import xarray as xr

PSEUDO_ABSENCES_PATH = "data/processed/pseudo_absences_final.csv"
GRID_PATH = "data/processed/analysis_grid.geojson"
CACHE_DIR = Path("data/external/era5land_cache")
EXTRACTED_DIR = CACHE_DIR / "extracted"
OUTPUT_PATH = "data/processed/meteorology_features_pseudo_absence.csv"
UTM_CRS = "EPSG:32736"
WGS84_CRS = "EPSG:4326"

AREA = [1.0, 34.2, -1.0, 35.6]


def get_nc_path(zip_or_nc_path, year, month):
    with open(zip_or_nc_path, "rb") as f:
        header = f.read(4)
    if header == b"PK\x03\x04":
        extract_target_dir = EXTRACTED_DIR / f"{year}_{month:02d}"
        if not extract_target_dir.exists():
            extract_target_dir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(zip_or_nc_path, "r") as zf:
                zf.extractall(extract_target_dir)
        nc_files = list(extract_target_dir.glob("*.nc"))
        return nc_files[0] if nc_files else None
    return zip_or_nc_path


def download_month(client, year, month, days):
    target = CACHE_DIR / f"era5land_{year}_{month:02d}.nc"
    if target.exists():
        return target
    request = {
        "variable": ["2m_temperature", "2m_dewpoint_temperature",
                     "10m_u_component_of_wind", "10m_v_component_of_wind"],
        "year": str(year), "month": f"{month:02d}",
        "day": [f"{d:02d}" for d in sorted(days)],
        "time": ["12:00"], "area": AREA, "data_format": "netcdf",
    }
    print(f"  Requesting {year}-{month:02d} ({len(days)} days)...")
    client.retrieve("reanalysis-era5-land", request, str(target))
    return target


def main():
    pa = pd.read_csv(PSEUDO_ABSENCES_PATH)
    pa["eventDate_parsed"] = pd.to_datetime(pa["eventDate"].astype(str).str[:10], format="%Y-%m-%d", errors="coerce")
    pa = pa.dropna(subset=["eventDate_parsed"])
    print(f"Pseudo-absence records: {len(pa)}")

    unique_dates = set()
    for obs_date in pa["eventDate_parsed"]:
        for days_back in range(7):
            unique_dates.add((obs_date - timedelta(days=days_back)).date())

    year_month_days = defaultdict(set)
    for d in unique_dates:
        year_month_days[(d.year, d.month)].add(d.day)
    print(f"Unique (year, month) combinations needed: {len(year_month_days)}")

    client = cdsapi.Client()
    downloaded_files = {}
    for (year, month), days in sorted(year_month_days.items()):
        target = download_month(client, year, month, days)
        downloaded_files[(year, month)] = target

    print(f"\nAll months ready ({len(downloaded_files)} total, cached + newly downloaded).")

    grid = gpd.read_file(GRID_PATH)
    grid_utm = grid.to_crs(UTM_CRS)
    centroids_utm = grid_utm.geometry.centroid
    centroids_gdf = gpd.GeoDataFrame(
        {"grid_cell_id": grid["grid_cell_id"]}, geometry=centroids_utm, crs=UTM_CRS
    ).to_crs(WGS84_CRS)
    centroids_gdf["lat"] = centroids_gdf.geometry.y
    centroids_gdf["lon"] = centroids_gdf.geometry.x
    centroids = centroids_gdf.set_index("grid_cell_id")

    results = []
    for idx, (_, row) in enumerate(pa.iterrows(), 1):
        cell_id = row["grid_cell_id"]
        if cell_id not in centroids.index:
            continue
        lat, lon = centroids.loc[cell_id, "lat"], centroids.loc[cell_id, "lon"]
        obs_date = row["eventDate_parsed"]

        daily_temps, daily_dewpoints, daily_winds = [], [], []
        same_day_temp = same_day_dewpoint = same_day_wind = None

        for days_back in range(7):
            d = (obs_date - timedelta(days=days_back)).date()
            key = (d.year, d.month)
            if key not in downloaded_files:
                continue
            nc_path = get_nc_path(downloaded_files[key], d.year, d.month)
            if nc_path is None:
                continue

            ds = xr.open_dataset(nc_path)
            try:
                point = ds.sel(latitude=lat, longitude=lon, method="nearest")
                time_dim = "valid_time" if "valid_time" in ds.dims else "time"
                day_data = point.sel({time_dim: pd.Timestamp(d)}, method="nearest")

                t2m = float(day_data["t2m"].values) - 273.15
                d2m = float(day_data["d2m"].values) - 273.15
                u10 = float(day_data["u10"].values)
                v10 = float(day_data["v10"].values)
                wind_speed = (u10**2 + v10**2) ** 0.5

                daily_temps.append(t2m)
                daily_dewpoints.append(d2m)
                daily_winds.append(wind_speed)
                if days_back == 0:
                    same_day_temp, same_day_dewpoint, same_day_wind = t2m, d2m, wind_speed
            except Exception:
                pass
            finally:
                ds.close()

        results.append({
            "record_key": row["key"],
            "grid_cell_id": cell_id,
            "observation_date": obs_date.date(),
            "temp_mean_7d": round(sum(daily_temps) / len(daily_temps), 2) if daily_temps else None,
            "dewpoint_mean_7d": round(sum(daily_dewpoints) / len(daily_dewpoints), 2) if daily_dewpoints else None,
            "wind_mean_7d": round(sum(daily_winds) / len(daily_winds), 2) if daily_winds else None,
            "temp_same_day": round(same_day_temp, 2) if same_day_temp is not None else None,
            "dewpoint_same_day": round(same_day_dewpoint, 2) if same_day_dewpoint is not None else None,
            "wind_same_day": round(same_day_wind, 2) if same_day_wind is not None else None,
            "days_with_data": len(daily_temps),
        })

        if idx % 20 == 0 or idx == len(pa):
            print(f"  [{idx}/{len(pa)}] records processed...")

    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nExtracted meteorology for {len(results_df)} pseudo-absence records.")
    print(f"Incomplete (days_with_data < 7): {(results_df['days_with_data'] < 7).sum()}")
    print(f"Saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
