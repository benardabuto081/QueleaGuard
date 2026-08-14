"""
Milestone 4.5 (Stage 2) - Inspect completed AppEEARS NDVI bundle.

Purpose:
    Inspect the files produced by the completed v2 45-cell AppEEARS
    task before downloading anything.

Task:
    queleaguard_ndvi_pa_v2_gap_45cells

Task ID:
    be74e08a-bee5-4418-acd1-e024b3582f93

IMPORTANT:
    This script only lists the bundle contents.
    It does NOT download or modify any data.
"""

import getpass
import requests

APPEEARS_API = "https://appeears.earthdatacloud.nasa.gov/api"
TASK_ID = "be74e08a-bee5-4418-acd1-e024b3582f93"


def login():
    username = input("Earthdata username: ")
    password = getpass.getpass("Earthdata password (hidden as you type): ")

    response = requests.post(
        f"{APPEEARS_API}/login",
        auth=(username, password),
        timeout=30,
    )

    response.raise_for_status()
    return response.json()["token"]


def main():
    print("=" * 70)
    print("QueleaGuard Milestone 4.5 - AppEEARS Bundle Inspection")
    print("=" * 70)
    print(f"Task ID: {TASK_ID}")
    print()

    token = login()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(
        f"{APPEEARS_API}/bundle/{TASK_ID}",
        headers=headers,
        timeout=30,
    )

    print(f"HTTP status: {response.status_code}")
    response.raise_for_status()

    bundle = response.json()

    print("\n=== Bundle keys ===")
    print(bundle.keys())

    files = bundle.get("files", [])

    print(f"\n=== Files returned: {len(files)} ===")

    for i, item in enumerate(files, start=1):
        print(f"\n[{i}]")
        print(f"file_name : {item.get('file_name')}")
        print(f"file_id   : {item.get('file_id')}")
        print(f"file_size : {item.get('file_size')}")
        print(f"file_type : {item.get('file_type')}")

    print("\n=== Candidate result files ===")

    result_files = [
        item for item in files
        if item.get("file_name", "").endswith("-results.csv")
    ]

    if result_files:
        for item in result_files:
            print(
                f"RESULT CSV: {item.get('file_name')} "
                f"(file_id={item.get('file_id')})"
            )
    else:
        print("WARNING: No *-results.csv file found.")

    print("\nInspection complete.")
    print("NO FILES WERE DOWNLOADED OR MODIFIED.")


if __name__ == "__main__":
    main()
