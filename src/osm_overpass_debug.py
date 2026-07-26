import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

QUERY = """
[out:json][timeout:60];
(
  node["name"~"Nyamware",i](around:20000, -0.1496144, 34.9263121);
  way["name"~"Nyamware",i](around:20000, -0.1496144, 34.9263121);
  relation["name"~"Nyamware",i](around:20000, -0.1496144, 34.9263121);
);
out center tags;
"""

response = requests.post(OVERPASS_URL, data={"data": QUERY}, timeout=90)
print(f"Status code: {response.status_code}")
print("Response body:")
print(response.text[:2000])
