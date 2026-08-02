"""
Milestone 3.4 (rebuilt) - Resumable CHIRPS daily raster cache downloader.

Downloads every unique daily CHIRPS GeoTIFF needed to cover all 90-day
antecedent windows across the 133 modelling-candidate records (3,247
unique dates, per diagnostic script), caching them locally so the
download never needs to repeat once complete.

Safe to interrupt (Ctrl+C) and re-run - already-downloaded files are
skipped automatically.

Cache location: data/external/chirps_cache/
"""

import time
import requests
from pathlib import Path
import pandas as pd
from datetime import timedelta

OCCURRENCES_PATH = "data/processed/occurrences_with_grid_cell.csv"
CACHE_DIR = Path("data/external/chirps_cache")
CHIRPS_BASE = "https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05"


def get_needed_dates():
    df = pd.read_csv(OCCURRENCES_PATH)
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    candidates = df[(df["year"] >= 2000) & (df["grid_cell_id"].notna())].copy()
    candidates["eventDate_clean"] = candidates["eventDate"].str[:10]
    candidates["eventDate_parsed"] = pd.to_datetime(
        candidates["eventDate_clean"], format="%Y-%m-%d", errors="coerce"
    )
    candidates = candidates.dropna(subset=["eventDate_parsed"])

    unique_dates = set()
    for obs_date in candidates["eventDate_parsed"]:
        for days_back in range(91):
            unique_dates.add((obs_date - timedelta(days=days_back)).date())

    return sorted(unique_dates)


def download_one(date_obj, session):
    year = date_obj.year
    filename = f"chirps-v2.0.{date_obj:%Y.%m.%d}.tif.gz"
    local_path = CACHE_DIR / str(year) / filename

    if local_path.exists() and local_path.stat().st_size > 0:
        return "cached"

    local_path.parent.mkdir(parents=True, exist_ok=True)
    url = f"{CHIRPS_BASE}/{year}/{filename}"

    for attempt in range(3):
        try:
            response = session.get(url, timeout=60)
            if response.status_code == 404:
                return "not_found"  # some dates may not have a file (rare gaps)
            response.raise_for_status()
            local_path.write_bytes(response.content)
            return "downloaded"
        except Exception:
            if attempt == 2:
                return "failed"
            time.sleep(3)


def main():
    dates = get_needed_dates()
    print(f"Total unique dates needed: {len(dates)}")

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()

    counts = {"cached": 0, "downloaded": 0, "failed": 0, "not_found": 0}
    for i, date_obj in enumerate(dates, 1):
        result = download_one(date_obj, session)
        counts[result] += 1

        if result == "downloaded" or i % 50 == 0 or i == len(dates):
            print(f"[{i}/{len(dates)}] {date_obj} -> {result} "
                  f"(cached: {counts['cached']}, downloaded: {counts['downloaded']}, "
                  f"failed: {counts['failed']}, not_found: {counts['not_found']})")

    print("\nDownload pass complete.")
    print(counts)
    if counts["failed"] > 0:
        print(f"\n{counts['failed']} files failed - simply re-run this script to retry them.")


if __name__ == "__main__":
    main()
