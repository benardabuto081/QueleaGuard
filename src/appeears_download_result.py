"""
Milestone 2.6 (continued) - Download completed AppEEARS NDVI result and
inspect real values.

Output: data/external/appeears_ahero_ndvi_pilot.csv
        reports/milestone_2_6_ndvi_pilot_result.txt
"""

import getpass
import requests
import pandas as pd

APPEEARS_API = "https://appeears.earthdatacloud.nasa.gov/api"
TASK_ID = "94425b98-8b7c-4670-a8ab-680569e0b896"


def login():
    username = input("Earthdata username: ")
    password = getpass.getpass("Earthdata password (hidden as you type): ")
    response = requests.post(f"{APPEEARS_API}/login", auth=(username, password), timeout=30)
    response.raise_for_status()
    return response.json()["token"]


def main():
    token = login()
    headers = {"Authorization": f"Bearer {token}"}

    # List available output files for this task
    response = requests.get(f"{APPEEARS_API}/bundle/{TASK_ID}", headers=headers, timeout=30)
    response.raise_for_status()
    files = response.json()["files"]

    # Find the main results CSV (AppEEARS names it something like *-results.csv)
    csv_file = next(f for f in files if f["file_name"].endswith("-results.csv"))
    file_id = csv_file["file_id"]

    print(f"Downloading: {csv_file['file_name']}")
    download_response = requests.get(
        f"{APPEEARS_API}/bundle/{TASK_ID}/{file_id}", headers=headers, timeout=60
    )
    download_response.raise_for_status()

    output_path = "data/external/appeears_ahero_ndvi_pilot.csv"
    with open(output_path, "wb") as f:
        f.write(download_response.content)
    print(f"Saved to {output_path}")

    df = pd.read_csv(output_path)
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nFirst few rows:")
    print(df.head())

    ndvi_col = [c for c in df.columns if "NDVI" in c][0]
    result_summary = f"""Milestone 2.6 - MODIS NDVI (AppEEARS) Access Pilot
=====================================================

Product: MOD13Q1.061, 250m, 16-day composite NDVI
Location: Ahero Irrigation Scheme ({AHERO_LAT if False else -0.1496144}, 34.9263121)
Period: January 2024
Access method: NASA AppEEARS point-extraction API (asynchronous task queue),
authenticated via NASA Earthdata login
Rows retrieved: {len(df)}
NDVI column: {ndvi_col}
Sample NDVI values: {df[ndvi_col].head(3).tolist()}

Conclusion: MODIS NDVI access via AppEEARS confirmed feasible. Task processed
quickly (well under the multi-hour worst case). Values require scaling per
MOD13Q1 product documentation (raw NDVI is typically scaled by 0.0001) before
use - to be handled in Milestone 3 preprocessing, not this pilot.
"""
    with open("reports/milestone_2_6_ndvi_pilot_result.txt", "w") as f:
        f.write(result_summary)
    print("\nSaved reference result to reports/milestone_2_6_ndvi_pilot_result.txt")


if __name__ == "__main__":
    main()
