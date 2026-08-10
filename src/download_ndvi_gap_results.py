"""
Milestone 3.9/3.10 - Download the completed NDVI gap-fill task results
(43 grid cells needed by pseudo-absence records, not covered by the
original Milestone 3.6 extraction).

Output: data/external/appeears_ndvi_pseudo_absence_gap.csv
"""

import getpass
import requests

APPEEARS_API = "https://appeears.earthdatacloud.nasa.gov/api"
TASK_ID = "0889d6bb-d49a-44c5-9a41-239ee27bff4f"
OUTPUT_PATH = "data/external/appeears_ndvi_pseudo_absence_gap.csv"


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

    import pandas as pd
    df = pd.read_csv(OUTPUT_PATH)
    print(f"Rows: {len(df)}")
    print(f"Unique cells: {df['ID'].nunique()}")


if __name__ == "__main__":
    main()
