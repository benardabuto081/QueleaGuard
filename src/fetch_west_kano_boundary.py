"""
Fetch the West Kano Irrigation Scheme polygon geometry from OpenStreetMap
via Overpass API, for comparison against the rice raster footprint.

Output: data/external/west_kano_boundary.geojson
"""

import requests
import json

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
HEADERS = {"User-Agent": "QueleaGuard-Capstone-Research/1.0"}

QUERY = """
[out:json][timeout:60];
way["landuse"="farmland"]["name"~"West Kano",i](around:5000, -0.2028815, 34.8124258);
out geom;
"""


def main():
    response = requests.post(OVERPASS_URL, data={"data": QUERY}, headers=HEADERS, timeout=90)
    response.raise_for_status()
    data = response.json()

    elements = data.get("elements", [])
    print(f"Found {len(elements)} matching feature(s).")

    if not elements:
        print("No polygon found by name filter.")
        return

    way = elements[0]
    tags = way.get("tags", {})
    geometry = way.get("geometry", [])
    print(f"Feature tags: {tags}")
    print(f"Number of boundary points: {len(geometry)}")

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

    output_path = "data/external/west_kano_boundary.geojson"
    with open(output_path, "w") as f:
        json.dump(geojson, f, indent=2)
    print(f"\nSaved to {output_path}")


if __name__ == "__main__":
    main()
