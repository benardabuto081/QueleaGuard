import requests
import time

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "QueleaGuard-Capstone-Research/1.0"}

QUERIES = [
    "West Kano Irrigation Scheme, Kenya",
    "South West Kano Irrigation Scheme, Kenya",
    "Kano Plains, Kisumu, Kenya",
    "Kadibo, Kisumu, Kenya",
    "Nyando, Kisumu, Kenya",
]


def search(query: str) -> list:
    response = requests.get(
        NOMINATIM_URL,
        params={
            "q": query,
            "format": "json",
            "polygon_geojson": 1,
            "addressdetails": 1,
            "limit": 3,
        },
        headers=HEADERS,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def main():
    for query in QUERIES:
        print("=" * 60)
        print(f"QUERY: {query}")
        print("=" * 60)
        results = search(query)

        if not results:
            print("No results found.\n")
        else:
            for r in results:
                has_polygon = "geojson" in r and r["geojson"].get("type") in ("Polygon", "MultiPolygon")
                print(f"- Name: {r.get('display_name')}")
                print(f"  OSM type: {r.get('osm_type')} | class/type: {r.get('class')}/{r.get('type')}")
                print(f"  Lat/Lon: {r.get('lat')}, {r.get('lon')}")
                print(f"  Bounding box: {r.get('boundingbox')}")
                print(f"  Has polygon geometry: {has_polygon}")
                print()

        time.sleep(1)


if __name__ == "__main__":
    main()
