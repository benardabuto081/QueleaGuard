"""
Milestone 2.6 - MODIS NDVI access pilot, part 1: authenticate and submit
a point-based NDVI extraction request via NASA AppEEARS.

Prompts for Earthdata username/password interactively (not stored anywhere)
to avoid writing credentials to disk or exposing them elsewhere.

AppEEARS processes requests asynchronously - this script only submits the
task and saves the task ID. A separate script will check status and download
results once processing completes.

Output: reports/milestone_2_6_appeears_task_id.txt
"""

import getpass
import requests

APPEEARS_API = "https://appeears.earthdatacloud.nasa.gov/api"

AHERO_LAT = -0.1496144
AHERO_LON = 34.9263121


def login():
    username = input("Earthdata username: ")
    password = getpass.getpass("Earthdata password (hidden as you type): ")
    response = requests.post(f"{APPEEARS_API}/login", auth=(username, password), timeout=30)
    response.raise_for_status()
    token = response.json()["token"]
    print("Login successful, token acquired.")
    return token


def submit_task(token):
    headers = {"Authorization": f"Bearer {token}"}

    task = {
        "task_type": "point",
        "task_name": "queleaguard_ahero_ndvi_pilot",
        "params": {
            "dates": [{"startDate": "01-01-2024", "endDate": "01-31-2024"}],
            "layers": [{"product": "MOD13Q1.061", "layer": "_250m_16_days_NDVI"}],
            "coordinates": [
                {"id": "ahero", "latitude": AHERO_LAT, "longitude": AHERO_LON, "category": "Ahero Irrigation Scheme"}
            ],
        },
    }

    response = requests.post(f"{APPEEARS_API}/task", json=task, headers=headers, timeout=30)
    response.raise_for_status()
    task_id = response.json()["task_id"]
    print(f"Task submitted successfully. Task ID: {task_id}")
    return task_id


def main():
    token = login()
    task_id = submit_task(token)

    with open("reports/milestone_2_6_appeears_task_id.txt", "w") as f:
        f.write(f"AppEEARS task ID: {task_id}\n")
        f.write("Submitted for: MOD13Q1.061 NDVI, Ahero coordinates, Jan 2024\n")
        f.write("Check status with src/appeears_check_status.py before downloading.\n")

    print("\nTask ID saved to reports/milestone_2_6_appeears_task_id.txt")
    print("AppEEARS processing can take anywhere from minutes to a few hours.")
    print("We'll check status in a separate step.")


if __name__ == "__main__":
    main()
