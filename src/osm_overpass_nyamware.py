"""
Milestone 2.1 (continued) - Retry Nyamware Overpass search with backoff,
against the main Overpass instance (retrying after the mirror timed out).
"""

import requests
import time

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
HEADERS = {"User-Agent": "QueleaGuard-Capstone-Research/1.0"}

QUERY = """
[out:json][timeout:90];
(
  node["name"~"Nyamware",i](around:20000, -0.1496144, 34.9263121);
  way["name"~"Nyamware",i](around:20000, -0.1496144, 34.9263121);
  relation["name"~"Nyamware",i](around:20000, -0.1496144, 34.9263121);
);
out center tags;
"""


def main():
    for attempt in range(1, 4):
        print(f"Attempt {attempt}...")
        try:
            response = requests.post(
                OVERPASS_URL, data={"data": QUERY}, headers=HEADERS, timeout=100
            )
            if response.status_code == 200:
                data = response.json()
                elements = data.get("elements", [])
                print(f"Success. Found {len(elements)} matching feature(s).\n")
                for el in elements:
                    tags = el.get("tags", {})
                    lat = el.get("lat") or el.get("center", {}).get("lat")
                    lon = el.get("lon") or el.get("center", {}).get("lon")
                    print(f"Type: {el.get('type')} | Name: {tags.get('name')}")
                    print(f"  Tags: {tags}")
                    print(f"  Location: {lat}, {lon}\n")
                return
            else:
                print(f"Status {response.status_code}, retrying in 10s...")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}, retrying in 10s...")

        time.sleep(10)

    print("All attempts failed. Overpass is not responding reliably right now.")


if __name__ == "__main__":
    main()
