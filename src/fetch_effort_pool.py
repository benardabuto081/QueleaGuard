"""
Milestone 3.9 (corrected) - Rebuild the effort-proxy pool by querying
GBIF proportionally across the years represented in our presence data,
fixing the temporal skew caused by GBIF's default result ordering
(all-recent-records-first) in the original uncontrolled pull.

Output: data/raw/gbif_all_species_effort_pool.csv (overwritten, corrected)
"""

import time
import requests
import pandas as pd
import geopandas as gpd

GBIF_API_BASE = "https://api.gbif.org/v1"
GRID_PATH = "data/processed/analysis_grid.geojson"
OCCURRENCES_PATH = "data/processed/occurrences_with_grid_cell.csv"
OUTPUT_PATH = "data/raw/gbif_all_species_effort_pool.csv"
RECORDS_PER_YEAR = 150  # target records per year - proportional coverage, not volume

FIELDS = [
    "key", "scientificName", "decimalLatitude", "decimalLongitude",
    "eventDate", "year", "month", "day", "basisOfRecord", "datasetKey",
]


def fetch_year_with_retry(lat_range, lon_range, year, max_records, retries=4):
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
    grid = gpd.read_file(GRID_PATH)
    minx, miny, maxx, maxy = grid.total_bounds
    lat_range = f"{miny:.4f},{maxy:.4f}"
    lon_range = f"{minx:.4f},{maxx:.4f}"

    occ = pd.read_csv(OCCURRENCES_PATH)
    occ["year"] = pd.to_numeric(occ["year"], errors="coerce")
    presence_years = sorted(occ[occ["year"] >= 2000]["year"].dropna().unique().astype(int))
    print(f"Years to cover (matching presence record years): {presence_years}")

    all_records = []
    for year in presence_years:
        print(f"Querying year {year}...")
        year_records = fetch_year_with_retry(lat_range, lon_range, year, RECORDS_PER_YEAR)
        print(f"  Retrieved {len(year_records)} records for {year}")
        all_records.extend(year_records)

    print(f"\nTotal records across all years: {len(all_records)}")

    rows = [{f: rec.get(f) for f in FIELDS} for rec in all_records]
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved to {OUTPUT_PATH}")

    print(f"\nYear distribution in corrected pool:")
    print(df["year"].value_counts().sort_index())


if __name__ == "__main__":
    main()
