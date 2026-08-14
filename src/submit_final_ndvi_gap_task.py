from pathlib import Path
import getpass
import json
import sys

import pandas as pd
import requests


# =============================================================================
# QUELEAGUARD - SUBMIT FINAL 36-CELL NDVI GAP TASK
# =============================================================================

ROOT = Path(__file__).resolve().parents[1]

SPEC_PATH = ROOT / "data" / "processed" / "ndvi_second_task_spec.csv"

APPEEARS_API = "https://appeears.earthdatacloud.nasa.gov/api"

TASK_NAME = "queleaguard_ndvi_final_gap_36cells"

PRODUCT = "MOD13Q1.061"
LAYER = "_250m_16_days_NDVI"

# AppEEARS requires MM-DD-YYYY.
START_DATE = "01-01-2000"
END_DATE = "08-14-2026"


# =============================================================================
# HELPERS
# =============================================================================

def fail(message):
    print()
    print("=" * 80)
    print("FAILED")
    print("=" * 80)
    print(message)
    sys.exit(1)


# =============================================================================
# HEADER
# =============================================================================

print("=" * 80)
print("QUELEAGUARD - SUBMIT FINAL 36-CELL NDVI GAP TASK")
print("=" * 80)
print()


# =============================================================================
# LOAD SPECIFICATION
# =============================================================================

print(f"Specification: {SPEC_PATH}")

if not SPEC_PATH.exists():
    fail(f"Task specification not found:\n{SPEC_PATH}")

spec = pd.read_csv(SPEC_PATH)

required_columns = {
    "grid_cell_id",
    "latitude",
    "longitude",
}

missing_columns = required_columns - set(spec.columns)

if missing_columns:
    fail(
        "Missing required columns:\n"
        + ", ".join(sorted(missing_columns))
    )

print(f"Cells:         {len(spec):,}")
print(f"Product:       {PRODUCT}")
print(f"Layer:         {LAYER}")
print(f"Date range:    {START_DATE} -> {END_DATE}")


# =============================================================================
# VALIDATE SPECIFICATION
# =============================================================================

print()
print("=" * 80)
print("FINAL TASK VALIDATION")
print("=" * 80)

if len(spec) != 36:
    fail(
        f"Expected 36 cells, found {len(spec)}."
    )

print("[PASS] Exactly 36 cells")

if spec["grid_cell_id"].duplicated().any():
    fail("Duplicate grid_cell_id values detected.")

print("[PASS] No duplicate cells")

if spec["latitude"].isna().any() or spec["longitude"].isna().any():
    fail("Missing coordinate values detected.")

print("[PASS] All coordinates present")

if not spec["latitude"].between(-90, 90).all():
    fail("Invalid latitude detected.")

if not spec["longitude"].between(-180, 180).all():
    fail("Invalid longitude detected.")

print("[PASS] Coordinates valid")

print("[PASS] MOD13Q1.061")
print("[PASS] NDVI layer")
print("[PASS] Point task")
print("[PASS] Date format MM-DD-YYYY")


# =============================================================================
# BUILD COORDINATES
# =============================================================================

coordinates = []

for _, row in spec.iterrows():
    coordinates.append(
        {
            "id": str(row["grid_cell_id"]),
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
        }
    )


# =============================================================================
# DISPLAY CELLS
# =============================================================================

print()
print("=" * 80)
print("36 CELLS TO BE SUBMITTED")
print("=" * 80)

print(
    spec[
        [
            "grid_cell_id",
            "latitude",
            "longitude",
        ]
    ].to_string(index=False)
)


# =============================================================================
# BUILD TASK
# =============================================================================

task = {
    "task_type": "point",
    "task_name": TASK_NAME,
    "params": {
        "dates": [
            {
                "startDate": START_DATE,
                "endDate": END_DATE,
            }
        ],
        "layers": [
            {
                "product": PRODUCT,
                "layer": LAYER,
            }
        ],
        "coordinates": coordinates,
        "output": {
            "format": {
                "type": "csv"
            },
            "projection": "geographic"
        }
    }
}


# =============================================================================
# FINAL REQUEST VALIDATION
# =============================================================================

print()
print("=" * 80)
print("FINAL REQUEST VALIDATION")
print("=" * 80)

assert task["task_type"] == "point"
assert task["task_name"] == TASK_NAME
assert "coordinates" in task["params"]
assert len(task["params"]["coordinates"]) == 36
assert len(task["params"]["layers"]) == 1
assert task["params"]["layers"][0]["product"] == PRODUCT
assert task["params"]["layers"][0]["layer"] == LAYER
assert task["params"]["dates"][0]["startDate"] == START_DATE
assert task["params"]["dates"][0]["endDate"] == END_DATE

print("[PASS] Point task")
print("[PASS] Task name")
print("[PASS] 36 coordinates")
print("[PASS] Coordinates under params")
print("[PASS] MOD13Q1.061")
print("[PASS] _250m_16_days_NDVI")
print("[PASS] 01-01-2000 -> 08-14-2026")


# =============================================================================
# LOGIN
# =============================================================================

print()
print("=" * 80)
print("APPEEARS LOGIN")
print("=" * 80)

username = input("AppEEARS / Earthdata username: ").strip()
password = getpass.getpass("AppEEARS / Earthdata password: ")

if not username or not password:
    fail("Username and password are required.")


# =============================================================================
# AUTHENTICATE
# =============================================================================
#
# IMPORTANT:
# This is the authentication method just proven to return HTTP 200.
# =============================================================================

try:
    auth_response = requests.post(
        f"{APPEEARS_API}/login",
        auth=(username, password),
        timeout=60,
    )
except requests.RequestException as exc:
    fail(f"Authentication request failed:\n{exc}")

print(f"Authentication HTTP status: {auth_response.status_code}")

if auth_response.status_code != 200:
    print(auth_response.text)
    fail("AppEEARS authentication failed.")

try:
    auth_data = auth_response.json()
except ValueError:
    fail(
        "Authentication response was not valid JSON:\n"
        + auth_response.text
    )

token = auth_data.get("token")

if not token:
    fail(
        "Authentication succeeded but no token was returned:\n"
        + json.dumps(auth_data, indent=2)
    )

print("[PASS] AppEEARS authentication successful.")


# =============================================================================
# SUBMIT
# =============================================================================

print()
print("=" * 80)
print("SUBMITTING FINAL 36-CELL APPEEARS TASK")
print("=" * 80)

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
}

try:
    response = requests.post(
        f"{APPEEARS_API}/task",
        headers=headers,
        json=task,
        timeout=120,
    )
except requests.RequestException as exc:
    fail(f"Task submission request failed:\n{exc}")

print(f"HTTP status: {response.status_code}")


# =============================================================================
# HANDLE RESPONSE
# =============================================================================

try:
    response_data = response.json()
except ValueError:
    response_data = {
        "raw_response": response.text
    }


# =============================================================================
# SUCCESS
# =============================================================================

if response.status_code in (200, 201):

    print()
    print("=" * 80)
    print("SUCCESS - FINAL NDVI GAP TASK SUBMITTED")
    print("=" * 80)

    print(json.dumps(response_data, indent=2))

    response_path = (
        ROOT
        / "data"
        / "processed"
        / "ndvi_final_gap_task_submission_response.json"
    )

    submission_record = {
        "task_name": TASK_NAME,
        "task_type": "point",
        "product": PRODUCT,
        "layer": LAYER,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "cell_count": 36,
        "coordinates": coordinates,
        "appeears_response": response_data,
    }

    with open(response_path, "w", encoding="utf-8") as f:
        json.dump(
            submission_record,
            f,
            indent=2
        )

    print()
    print(f"Submission record saved:")
    print(response_path)

    print()
    print("=" * 80)
    print("ENGINEERING STATUS")
    print("=" * 80)
    print("[PASS] 36-cell NDVI gap task submitted")
    print("[PASS] Submission response archived")
    print()
    print("NEXT STEP: MONITOR APPEEARS TASK STATUS")
    print("Do NOT submit another NDVI task.")
    print("=" * 80)

    sys.exit(0)


# =============================================================================
# FAILURE
# =============================================================================

print()
print("=" * 80)
print("APPEEARS REJECTED THE TASK")
print("=" * 80)

print(json.dumps(response_data, indent=2))

print()
print("The task was NOT submitted successfully.")

sys.exit(1)
