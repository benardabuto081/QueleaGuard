"""
Milestone 3.6 (continued) - Check status of the 20-cell NDVI AppEEARS task.
"""

import getpass
import requests

APPEEARS_API = "https://appeears.earthdatacloud.nasa.gov/api"
TASK_ID = "28801afb-d2dc-4c7f-b999-72f567a455bf"


def login():
    username = input("Earthdata username: ")
    password = getpass.getpass("Earthdata password (hidden as you type): ")
    response = requests.post(f"{APPEEARS_API}/login", auth=(username, password), timeout=30)
    response.raise_for_status()
    return response.json()["token"]


def main():
    token = login()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{APPEEARS_API}/task/{TASK_ID}", headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()
    print(f"Task ID: {TASK_ID}")
    print(f"Status: {data.get('status')}")
    print(f"Task name: {data.get('task_name')}")


if __name__ == "__main__":
    main()
