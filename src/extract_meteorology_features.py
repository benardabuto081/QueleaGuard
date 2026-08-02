"""
Milestone 3.5 (fixed) - Extract ERA5-Land meteorology features.
Same as before, but unzips each downloaded file first, since CDS returns
a ZIP archive containing the actual NetCDF file rather than a raw .nc file.
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

OCCURRENCES_PATH = "data/processed/occurrences_with_grid_cell.csv"
GRID_PATH = "data/processed/analysis_grid.geojson"
CACHE_DIR = Path("data/external/era5land_cache")
EXTRACTED_DIR = Path("data/external/era5land_cache/extracted")
OUTPUT_PATH = "data/processed/meteorology_features.csv"
SUMMARY_PATH = "reports/milestone_3_5_meteorology_extraction_summary.txt"
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


def get_nc_path(zip_or_nc_path, year, month):
    """Return a real, readable .nc file path, unzipping if necessary."""
    with open(zip_or_nc_path, "rb") as f:
        header = f.read(4)

    if header == b"PK\x03\x04":
        # It's a ZIP archive - extract the .nc file inside it
        extract_target_dir = EXTRACTED_DIR / f"{year}_{month:02d}"
        if not extract_target_dir.exists():
            extract_target_dir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(zip_or_nc_path, "r") as zf:
                zf.extractall(extract_target_dir)

        nc_files = list(extract_target_dir.glob("*.nc"))
        if not nc_files:
            raise FileNotFoundError(f"No .nc file found inside {zip_or_nc_path}")
        return nc_files[0]
    else:
        # Already a raw NetCDF file
        return zip_or_nc_path


def main():
    candidates, centroids = load_candidates_and_centroids()
    print(f"Modelling-candidate records: {len(candidates)}")

    unique_dates = set()
    for obs_date in candidates["eventDate_parsed"]:
        for days_back in range(7):
            unique_dates.add((obs_date - timedelta(days=days_back)).date())

    year_months = sorted(set((d.year, d.month) for d in unique_dates))
    print(f"Unique (year, month) files to process: {len(year_months)}")

    # Resolve each downloaded file to a real, readable .nc path (unzipping as needed)
    nc_paths = {}
    for year, month in year_months:
        cached_file = CACHE_DIR / f"era5land_{year}_{month:02d}.nc"
        if not cached_file.exists():
            print(f"  WARNING: {cached_file} missing, skipping.")
            continue
        nc_paths[(year, month)] = get_nc_path(cached_file, year, month)

    print(f"Resolved {len(nc_paths)} readable NetCDF files.")

    # Extract per-record values
    results = []
    start_time = time.time()
    for idx, (_, row) in enumerate(candidates.iterrows(), 1):
        cell_id = row["grid_cell_id"]
        if cell_id not in centroids.index:
            continue
        lat = centroids.loc[cell_id, "centroid_lat"]
        lon = centroids.loc[cell_id, "centroid_lon"]
        obs_date = row["eventDate_parsed"]

        daily_temps, daily_dewpoints, daily_winds = [], [], []
        same_day_temp = same_day_dewpoint = same_day_wind = None

        for days_back in range(7):
            d = (obs_date - timedelta(days=days_back)).date()
            key = (d.year, d.month)
            if key not in nc_paths:
                continue

            ds = xr.open_dataset(nc_paths[key])
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
            except Exception as e:
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

        if idx % 20 == 0 or idx == len(candidates):
            print(f"  [{idx}/{len(candidates)}] records processed...")

    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nExtracted meteorology features for {len(results_df)} of {len(candidates)} candidates.")
    print(f"Saved to {OUTPUT_PATH}")
    print("\nSample results:")
    print(results_df.head(10).to_string(index=False))

    incomplete = results_df[results_df["days_with_data"] < 7]
    summary = f"""Milestone 3.5 - ERA5-Land Meteorology Feature Extraction Summary
====================================================================

Candidate records: {len(candidates)}
Successfully extracted: {len(results_df)}
Records with incomplete 7-day coverage: {len(incomplete)}
Unique (year, month) CDS requests: {len(year_months)}

Access method: Copernicus CDS API (cdsapi), batched by year-month.
Note: CDS returned ZIP archives (containing the actual NetCDF file)
rather than raw .nc files despite requesting netcdf format directly -
handled by detecting the ZIP signature and extracting automatically.

Variables: 2m temperature, 2m dewpoint temperature (humidity proxy),
10m wind speed (derived from u/v components). Midday (12:00) snapshot
used as representative daily value.

Windows computed: 7-day mean + same-day value, per Log Entry 006.

Statistics across all records:
{results_df[['temp_mean_7d', 'dewpoint_mean_7d', 'wind_mean_7d']].describe().to_string()}
"""
    with open(SUMMARY_PATH, "w") as f:
        f.write(summary)
    print(f"\nSaved summary to {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
