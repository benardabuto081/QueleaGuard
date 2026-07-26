"""
Milestone 2.1 - GBIF Occurrence Feasibility Check

Queries GBIF's public REST API directly for confirmed Quelea quelea occurrence
records at three progressively wider bounding boxes around Ahero/Nyamware,
Kisumu County, Kenya.

Note: calls the GBIF REST API directly with `requests` rather than via the
`pygbif` wrapper library, after encountering a compatibility bug in pygbif
0.6.6's species.name_backbone() function (it passes an incompatible keyword
argument through to the installed version of `requests`).

This is a read-only feasibility check (limit=0 returns only a record count,
no actual records are downloaded here). The result determines the Milestone 2.2
study-area decision per the Dataset Feasibility Study, Section 9.
"""

import requests

GBIF_API_BASE = "https://api.gbif.org/v1"


def get_species_key(scientific_name: str) -> dict:
    """Look up the GBIF taxon key for a scientific name."""
    response = requests.get(
        f"{GBIF_API_BASE}/species/match",
        params={"name": scientific_name},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def count_occurrences(taxon_key: int, lat_range: str, lon_range: str) -> int:
    """Return the number of occurrence records within a bounding box."""
    response = requests.get(
        f"{GBIF_API_BASE}/occurrence/search",
        params={
            "taxonKey": taxon_key,
            "decimalLatitude": lat_range,
            "decimalLongitude": lon_range,
            "limit": 0,  # limit=0 returns only the count, no records
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["count"]


def main():
    match = get_species_key("Quelea quelea")
    species_key = match["usageKey"]
    print(f"GBIF species match: {match.get('scientificName')}")
    print(f"GBIF usageKey: {species_key}")
    print(f"Match confidence: {match.get('confidence')}")
    print()

    bounding_boxes = {
        "tight_scheme_area (~15km buffer around Ahero/Nyamware)": {
            "lat": "-0.35,0.05",
            "lon": "34.75,35.05",
        },
        "kisumu_county (~50km buffer)": {
            "lat": "-0.7,0.5",
            "lon": "34.3,35.5",
        },
        "lake_victoria_basin (~200km buffer)": {
            "lat": "-3.0,1.5",
            "lon": "31.5,35.5",
        },
    }

    print("Occurrence record counts by bounding box:")
    print("-" * 60)
    for label, bbox in bounding_boxes.items():
        count = count_occurrences(species_key, bbox["lat"], bbox["lon"])
        print(f"{label}: {count} records")
    print("-" * 60)


if __name__ == "__main__":
    main()
