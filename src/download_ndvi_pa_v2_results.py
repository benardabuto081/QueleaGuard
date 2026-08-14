"""
Milestone 4.5 (Stage 2) - Download the completed 45-cell NDVI task results
via the authenticated AppEEARS bundle API (the same working pattern as
download_ndvi_gap_results.py) - NOT the public email download link, which
only serves the AppEEARS website HTML and was the source of the other
session's confusion.
"""

import getpass
import requests
import pandas as pd

APPEEARS_API = "https://appeears.earthdatacloud.nasa.gov/api"
TASK_ID = "be74e08a-bee5-4418-acd1-e024b3582f93"
OUTPUT_PATH = "data/external/appeears_ndvi_pa_v2_gap_45cells.csv"


def login():
    username = input("Earthdata username: ")
    password = getpass.getpass("Earthdata password (hidden as you type): ")
    response = requests.post(f"{APPEEARS_API}/login", auth=(username, password), timeout=30)
    response.raise_for_status()
    return response.json()["token"]


def main():
    token = login()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(f"{APPEEARS_API}/bundle/{TASK_ID}", headers=headers, timeout=30)
    response.raise_for_status()
    files = response.json()["files"]
    csv_file = next(f for f in files if f["file_name"].endswith("-results.csv"))
    file_id = csv_file["file_id"]

    print(f"Downloading: {csv_file['file_name']}")
    download_response = requests.get(f"{APPEEARS_API}/bundle/{TASK_ID}/{file_id}", headers=headers, timeout=120)
    download_response.raise_for_status()

    with open(OUTPUT_PATH, "wb") as f:
        f.write(download_response.content)
    print(f"Saved to {OUTPUT_PATH}")

    df = pd.read_csv(OUTPUT_PATH)
    print(f"Rows: {len(df)}")
    print(f"Unique cells: {df['ID'].nunique()} (should be 45)")


if __name__ == "__main__":
    main()
