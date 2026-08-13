"""
Milestone 4.4 (correction) - Rebuild the effort-proxy pool using explicit
year x month stratified GBIF queries, fixing the severe January-concentration
bug found in EDA (96.8% of pseudo-absence records fell in Jan/Feb, vs 20.3%
for presence). Root cause: the original fetch_effort_pool.py queried by
year only and capped at 150 records/year; GBIF's occurrence/search endpoint
has no documented default sort order, and empirically returned results
overwhelmingly front-loaded from January within most years (Year 2000, 2011,
2012 were literally 150/150 January). Filtering explicitly by month removes
the dependency on that undocumented ordering entirely.

This script also backs up the biased v1 files before overwriting them, for
full traceability of the methodological correction.

Output: data/raw/gbif_all_species_effort_pool.csv (rebuilt)
        data/raw/gbif_all_species_effort_pool_v1_month_skewed.csv (backup)
"""

import os
import shutil
import time
import requests
import pandas as pd
import geopandas as gpd

GBIF_API_BASE = "https://api.gbif.org/v1"
GRID_PATH = "data/processed/analysis_grid.geojson"
OCCURRENCES_PATH = "data/processed/occurrences_with_grid_cell.csv"
OUTPUT_PATH = "data/raw/gbif_all_species_effort_pool.csv"
BACKUP_PATH = "data/raw/gbif_all_species_effort_pool_v1_month_skewed.csv"
RECORDS_PER_YEAR_MONTH = 13  # ~150/12, spread evenly across all 12 months

FIELDS = [
    "key", "scientificName", "decimalLatitude", "decimalLongitude",
    "eventDate", "year", "month", "day", "basisOfRecord", "datasetKey",
]


def fetch_year_month_with_retry(lat_range, lon_range, year, month, max_records, retries=4):
    records = []
    offset = 0
    page_size = 300
    while len(records) < max_records:
        for attempt in range(1, retries + 1):
            try:
                response = requests.get(
                    f"{GBIF_API_BASE}/occurrence/search",
                    params={
                        "decimalLatitude": lat_range,
                        "decimalLongitude": lon_range,
                        "class": "Aves",
                        "year": year,
                        "month": month,
                        "limit": page_size,
                        "offset": offset,
                    },
                    timeout=60,
                )
                response.raise_for_status()
                data = response.json()
                break
            except Exception as e:
                print(f"      Attempt {attempt}/{retries} failed: {e}")
                if attempt < retries:
                    time.sleep(5 * attempt)
                else:
                    return records

        records.extend(data["results"])
        if data["endOfRecords"] or not data["results"]:
            break
        offset += page_size

    return records[:max_records]


def main():
    if os.path.exists(OUTPUT_PATH) and not os.path.exists(BACKUP_PATH):
        shutil.copy(OUTPUT_PATH, BACKUP_PATH)
        print(f"Backed up biased v1 pool to {BACKUP_PATH}")
    else:
        print("Backup already exists or no prior file found - skipping backup step.")

    grid = gpd.read_file(GRID_PATH)
    minx, miny, maxx, maxy = grid.total_bounds
    lat_range = f"{miny:.4f},{maxy:.4f}"
    lon_range = f"{minx:.4f},{maxx:.4f}"

    occ = pd.read_csv(OCCURRENCES_PATH)
    occ["year"] = pd.to_numeric(occ["year"], errors="coerce")
    presence_years = sorted(occ[occ["year"] >= 2000]["year"].dropna().unique().astype(int))
    print(f"Years to cover (matching presence record years): {presence_years}")
    print(f"Target: {RECORDS_PER_YEAR_MONTH} records per (year, month) pair, {len(presence_years)} years x 12 months = {len(presence_years) * 12} queries")

    all_records = []
    for year in presence_years:
        year_total = 0
        for month in range(1, 13):
            month_records = fetch_year_month_with_retry(lat_range, lon_range, year, month, RECORDS_PER_YEAR_MONTH)
            all_records.extend(month_records)
            year_total += len(month_records)
        print(f"Year {year}: {year_total} records across 12 months")

    print(f"\nTotal records across all (year, month) pairs: {len(all_records)}")

    rows = [{f: rec.get(f) for f in FIELDS} for rec in all_records]
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved to {OUTPUT_PATH}")

    print(f"\nMonth distribution in REBUILT pool:")
    print(df["month"].value_counts().sort_index())

    print(f"\nYear distribution in REBUILT pool:")
    print(df["year"].value_counts().sort_index())


if __name__ == "__main__":
    main()
