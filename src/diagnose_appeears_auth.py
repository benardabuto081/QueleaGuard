from getpass import getpass
import requests
import json

API = "https://appeears.earthdatacloud.nasa.gov/api"

print("=" * 80)
print("QUELEAGUARD - APPEEARS AUTHENTICATION DIAGNOSTIC")
print("=" * 80)
print()

username = input("AppEEARS / Earthdata username: ").strip()
password = getpass("AppEEARS / Earthdata password: ")

if not username or not password:
    print()
    print("[FAIL] Username and password are required.")
    raise SystemExit(1)

print()
print("=" * 80)
print("TEST 1 - APPEEARS API LOGIN")
print("=" * 80)

try:
    response = requests.post(
        f"{API}/login",
        auth=(username, password),
        timeout=60,
    )
except requests.RequestException as exc:
    print("[FAIL] Request error:")
    print(exc)
    raise SystemExit(1)

print(f"HTTP status: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type')}")

try:
    body = response.json()
    print("Response:")
    print(json.dumps(body, indent=2))
except ValueError:
    print("Response:")
    print(response.text[:2000])

if response.status_code == 200:
    print()
    print("=" * 80)
    print("[PASS] APPEEARS AUTHENTICATION SUCCESSFUL")
    print("=" * 80)
    print()
    print("We can proceed with the final 36-cell NDVI submission.")
else:
    print()
    print("=" * 80)
    print("[FAIL] APPEEARS AUTHENTICATION REJECTED")
    print("=" * 80)
    print()
    print("No NDVI task was submitted.")
