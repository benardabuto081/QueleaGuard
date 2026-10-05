import requests
import time
import json

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
HEADERS = {"User-Agent": "QueleaGuard-Capstone-Research/1.0"}

# Top 10 patches by area, from the earlier connected-component analysis
# (lat, lon, area_km2)
PATCHES = [
    (-0.1865, 34.8156, 4.258),
    (-0.2117, 34.8290, 2.172),
    (-0.2376, 34.8668, 2.132),
    (-0.1572, 34.9170, 2.123),
    (-0.1745, 34.8335, 1.391),
    (-0.1348, 34.9472, 1.164),
    (-0.2063, 34.8155, 1.156),
    (-0.2146, 34.8943, 0.922),
    (-0.1986, 34.9014, 0.881),
    (-0.1813, 34.8837, 0.861),
]


def reverse_geocode(lat, lon):
    response = requests.get(
        NOMINATIM_URL,
        params={"lat": lat, "lon": lon, "format": "json", "zoom": 16, "addressdetails": 1},
        headers=HEADERS,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def main():
    for rank, (lat, lon, area) in enumerate(PATCHES, 1):
        result = reverse_geocode(lat, lon)
        print(f"Patch {rank} ({area} km2) at ({lat}, {lon}):")
        print(f"  {result.get('display_name', 'NO RESULT')}")
        print()
        time.sleep(1)


if __name__ == "__main__":
    main()
