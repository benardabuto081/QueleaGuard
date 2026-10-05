import requests
import json

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
HEADERS = {"User-Agent": "QueleaGuard-Capstone-Research/1.0"}

QUERY = """
[out:json][timeout:60];
way["landuse"="farmland"]["operator"~"National Irrigation",i](-0.40,34.60,0.00,35.10);
out geom;
"""


def main():
    response = requests.post(OVERPASS_URL, data={"data": QUERY}, headers=HEADERS, timeout=90)
    response.raise_for_status()
    data = response.json()

    elements = data.get("elements", [])
    print(f"Found {len(elements)} NIA-operated farmland polygon(s) in the buffer.\n")

    for el in elements:
        tags = el.get("tags", {})
        geom = el.get("geometry", [])
        lons = [p["lon"] for p in geom]
        lats = [p["lat"] for p in geom]
        print(f"- Name: {tags.get('name', 'UNNAMED')}")
        print(f"  Crop: {tags.get('crop', 'n/a')}")
        print(f"  Approx bbox: lon [{min(lons):.4f}, {max(lons):.4f}], lat [{min(lats):.4f}, {max(lats):.4f}]")
        print()


if __name__ == "__main__":
    main()
