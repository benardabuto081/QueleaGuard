"""
Milestone 2.1 (continued) - Identify dominant source dataset and inspect
duplicate record clusters.
"""

import requests
import pandas as pd

INPUT_PATH = "data/raw/gbif_kisumu_county_raw.csv"
GBIF_API_BASE = "https://api.gbif.org/v1"


def get_dataset_name(dataset_key: str) -> str:
    response = requests.get(f"{GBIF_API_BASE}/dataset/{dataset_key}", timeout=30)
    response.raise_for_status()
    data = response.json()
    return f"{data.get('title')} (publisher: {data.get('publishingOrganizationKey')})"


def main():
    df = pd.read_csv(INPUT_PATH)

    print("=" * 60)
    print("TOP SOURCE DATASETS (by name)")
    print("=" * 60)
    top_datasets = df["datasetKey"].value_counts().head(3)
    for key, count in top_datasets.items():
        name = get_dataset_name(key)
        print(f"{count} records - {name}")
    print()

    print("=" * 60)
    print("SAMPLE OF DUPLICATE CLUSTERS (same lat/lon/date)")
    print("=" * 60)
    dupes = df[df.duplicated(subset=["decimalLatitude", "decimalLongitude", "eventDate"], keep=False)]
    grouped = dupes.groupby(["decimalLatitude", "decimalLongitude", "eventDate"])
    shown = 0
    for (lat, lon, date), group in grouped:
        if shown >= 5:
            break
        print(f"\nLocation ({lat}, {lon}) on {date} - {len(group)} records:")
        print(group[["recordedBy", "institutionCode", "occurrenceID"]].to_string(index=False))
        shown += 1


if __name__ == "__main__":
    main()
