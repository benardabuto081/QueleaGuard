"""
Milestone 3.10 (gap fix, continued) - Extend the CHIRPS cache to cover
pseudo-absence 90-day windows, which reach further back (into late 1999)
than the presence-only cache originally anticipated.
"""

import time
import requests
from pathlib import Path
import pandas as pd
from datetime import timedelta

PSEUDO_ABSENCES_PATH = "data/processed/pseudo_absences_final.csv"
CACHE_DIR = Path("data/external/chirps_cache")
CHIRPS_BASE = "https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05"


def get_needed_dates():
    pa = pd.read_csv(PSEUDO_ABSENCES_PATH)
    pa["parsed"] = pd.to_datetime(pa["eventDate"].astype(str).str[:10], format="%Y-%m-%d", errors="coerce")
    pa = pa.dropna(subset=["parsed"])

    unique_dates = set()
    for obs_date in pa["parsed"]:
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
                return "not_found"
            response.raise_for_status()
            local_path.write_bytes(response.content)
            return "downloaded"
        except Exception:
            if attempt == 2:
                return "failed"
            time.sleep(3)


def main():
    dates = get_needed_dates()
    print(f"Total unique dates needed for pseudo-absences: {len(dates)}")

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    counts = {"cached": 0, "downloaded": 0, "failed": 0, "not_found": 0}

    for i, date_obj in enumerate(dates, 1):
        result = download_one(date_obj, session)
        counts[result] += 1
        if result == "downloaded" or i % 100 == 0 or i == len(dates):
            print(f"[{i}/{len(dates)}] {date_obj} -> {result} | {counts}")

    print("\nDownload pass complete.")
    print(counts)
    if counts["failed"] > 0:
        print("Re-run this script to retry failed files.")


if __name__ == "__main__":
    main()
