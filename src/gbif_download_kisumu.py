"""
Milestone 2.1 (continued) - Download GBIF occurrence records for the
Kisumu County bounding box.

Pulls full record-level data (not just a count) so we can evaluate spatial
distribution, temporal coverage, coordinate uncertainty, basis of record,
and duplicates before any study-area decision is made.

Includes automatic retry with backoff, since the GBIF API connection has
shown intermittent drops during this session.

Output: data/raw/gbif_kisumu_county_raw.csv
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd

GBIF_API_BASE = "https://api.gbif.org/v1"
SPECIES_KEY = 2493987  # Quelea quelea, confirmed in Task 21/22

BBOX = {
    "lat": "-0.7,0.5",
    "lon": "34.3,35.5",
}

FIELDS = [
    "key",
    "scientificName",
    "decimalLatitude",
    "decimalLongitude",
    "eventDate",
    "year",
    "month",
    "day",
    "coordinateUncertaintyInMeters",
    "basisOfRecord",
    "datasetKey",
    "institutionCode",
    "recordedBy",
    "occurrenceID",
]


def build_session() -> requests.Session:
    """Create a requests session that retries on connection failures."""
    session = requests.Session()
    retry_strategy = Retry(
        total=5,
        backoff_factor=2,  # waits 2s, 4s, 8s, 16s, 32s between retries
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def fetch_all_records(session: requests.Session, taxon_key: int, lat_range: str, lon_range: str) -> list:
    """Fetch all occurrence records within a bounding box, handling pagination."""
    records = []
    offset = 0
    page_size = 300  # GBIF's max per-request limit

    while True:
        response = session.get(
            f"{GBIF_API_BASE}/occurrence/search",
            params={
                "taxonKey": taxon_key,
                "decimalLatitude": lat_range,
                "decimalLongitude": lon_range,
                "limit": page_size,
                "offset": offset,
            },
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        records.extend(data["results"])
        print(f"  Fetched {len(records)} records so far...")

        if data["endOfRecords"]:
            break
        offset += page_size

    return records


def main():
    session = build_session()

    print("Fetching all Quelea quelea records for Kisumu County bounding box...")
    raw_records = fetch_all_records(session, SPECIES_KEY, BBOX["lat"], BBOX["lon"])
    print(f"Retrieved {len(raw_records)} raw records.")

    rows = [{field: rec.get(field) for field in FIELDS} for rec in raw_records]
    df = pd.DataFrame(rows)

    output_path = "data/raw/gbif_kisumu_county_raw.csv"
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} records to {output_path}")


if __name__ == "__main__":
    main()
