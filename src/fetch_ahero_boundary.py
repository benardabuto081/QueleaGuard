"""
Milestone 3.1 - Fetch the actual Ahero Irrigation Scheme polygon geometry
from OpenStreetMap via Overpass API (not just the bounding box captured in
Milestone 2.1).

Output: data/external/ahero_boundary.geojson
"""

import requests
import json

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
HEADERS = {"User-Agent": "QueleaGuard-Capstone-Research/1.0"}

# Query for the specific farmland way identified in Milestone 2.1's Nominatim search
QUERY = """
[out:json][timeout:60];
way["landuse"="farmland"]["name"~"Ahero",i](around:5000, -0.1496144, 34.9263121);
out geom;
"""


def main():
    response = requests.post(OVERPASS_URL, data={"data": QUERY}, headers=HEADERS, timeout=90)
    response.raise_for_status()
    data = response.json()

    elements = data.get("elements", [])
    print(f"Found {len(elements)} matching feature(s).")

    if not elements:
        print("No polygon found by name filter - will retry with a broader query in the next step if needed.")
        return

    way = elements[0]
    tags = way.get("tags", {})
    geometry = way.get("geometry", [])
    print(f"Feature tags: {tags}")
    print(f"Number of boundary points: {len(geometry)}")

    # Convert OSM way geometry to GeoJSON Polygon format
    coordinates = [[point["lon"], point["lat"]] for point in geometry]
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": tags,
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coordinates],
                },
            }
        ],
    }

    output_path = "data/external/ahero_boundary.geojson"
    with open(output_path, "w") as f:
        json.dump(geojson, f, indent=2)
    print(f"\nSaved to {output_path}")


if __name__ == "__main__":
    main()
