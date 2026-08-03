"""
Milestone 3.8 (continued) - Retry Lake Victoria boundary fetch with
retry/backoff, since the full lake geometry is large and the connection
dropped mid-transfer on the first attempt.
"""

import time
import json
import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
HEADERS = {"User-Agent": "QueleaGuard-Capstone-Research/1.0"}
LAKE_QUERY = """
[out:json][timeout:120];
relation["natural"="water"]["name"~"Victoria",i](-1.0,34.0,0.5,35.6);
out geom;
"""


def main():
    for attempt in range(1, 6):
        try:
            print(f"Attempt {attempt}/5...")
            response = requests.post(OVERPASS_URL, data={"data": LAKE_QUERY}, headers=HEADERS, timeout=150)
            response.raise_for_status()
            data = response.json()
            break
        except Exception as e:
            print(f"  Failed: {e}")
            if attempt < 5:
                wait = 15 * attempt
                print(f"  Retrying in {wait}s...")
                time.sleep(wait)
            else:
                print("All attempts failed.")
                return

    elements = data.get("elements", [])
    print(f"Found {len(elements)} matching feature(s).")

    if not elements:
        print("WARNING: no Lake Victoria feature found.")
        return

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


if __name__ == "__main__":
    main()
