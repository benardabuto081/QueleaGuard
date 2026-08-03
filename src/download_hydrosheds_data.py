"""
Milestone 3.8 - Download HydroRIVERS Africa (river network) and fetch
Lake Victoria's boundary from OpenStreetMap (avoiding a 700MB+ global
HydroLAKES download for a single, already-locatable water body).

Output: data/external/hydrosheds_cache/HydroRIVERS_v10_af.gdb.zip
        data/external/lake_victoria.geojson
"""

import time
import requests
from pathlib import Path

CACHE_DIR = Path("data/external/hydrosheds_cache")
RIVERS_URL = "https://data.hydrosheds.org/file/HydroRIVERS/HydroRIVERS_v10_af.gdb.zip"
RIVERS_PATH = CACHE_DIR / "HydroRIVERS_v10_af.gdb.zip"

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
HEADERS = {"User-Agent": "QueleaGuard-Capstone-Research/1.0"}
LAKE_QUERY = """
[out:json][timeout:90];
relation["natural"="water"]["name"~"Victoria",i](-1.0,34.0,0.5,35.6);
out geom;
"""


def download_with_retry(url, dest_path, retries=5, timeout=180):
    for attempt in range(1, retries + 1):
        try:
            print(f"  Attempt {attempt}/{retries}...")
            response = requests.get(url, timeout=timeout, stream=True)
            response.raise_for_status()
            with open(dest_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    f.write(chunk)
            return True
        except Exception as e:
            print(f"    Failed: {e}")
            if attempt < retries:
                wait = 10 * attempt
                print(f"    Retrying in {wait}s...")
                time.sleep(wait)
    return False


def main():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if not RIVERS_PATH.exists() or RIVERS_PATH.stat().st_size < 1_000_000:
        print("Downloading HydroRIVERS Africa geodatabase (116MB)...")
        success = download_with_retry(RIVERS_URL, RIVERS_PATH)
        if success:
            print(f"Saved {RIVERS_PATH} ({RIVERS_PATH.stat().st_size/1e6:.1f} MB)")
        else:
            print("FAILED to download HydroRIVERS after all retries.")
    else:
        print(f"HydroRIVERS already cached: {RIVERS_PATH}")

    print("\nFetching Lake Victoria boundary from OpenStreetMap...")
    response = requests.post(OVERPASS_URL, data={"data": LAKE_QUERY}, headers=HEADERS, timeout=100)
    response.raise_for_status()
    data = response.json()
    elements = data.get("elements", [])
    print(f"Found {len(elements)} matching feature(s).")

    if elements:
        import json
        # Convert the largest matching relation to a simple GeoJSON polygon (outer ring only, for distance purposes)
        best = max(elements, key=lambda e: len(e.get("members", [])))
        coords = []
        for member in best.get("members", []):
            if member.get("role") == "outer" and "geometry" in member:
                coords.extend([[pt["lon"], pt["lat"]] for pt in member["geometry"]])

        if coords:
            geojson = {
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "properties": {"name": best.get("tags", {}).get("name", "Lake Victoria")},
                    "geometry": {"type": "LineString", "coordinates": coords},
                }],
            }
            with open("data/external/lake_victoria.geojson", "w") as f:
                json.dump(geojson, f)
            print(f"Saved Lake Victoria boundary ({len(coords)} points) to data/external/lake_victoria.geojson")
        else:
            print("WARNING: matched relation had no usable outer-ring geometry.")
    else:
        print("WARNING: no Lake Victoria feature found - will proceed with rivers only if this persists.")


if __name__ == "__main__":
    main()
