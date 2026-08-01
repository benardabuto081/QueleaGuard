"""
Milestone 2.6 (continued) - Check AppEEARS task status.

Run this periodically after submitting a task via appeears_submit_task.py.
Prompts for credentials again (tokens expire; not stored anywhere).
"""

import getpass
import requests

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

    response = requests.get(f"{APPEEARS_API}/task/{TASK_ID}", headers=headers, timeout=30)
    response.raise_for_status()
    status_data = response.json()

    print(f"Task ID: {TASK_ID}")
    print(f"Status: {status_data.get('status')}")
    print(f"Task name: {status_data.get('task_name')}")


if __name__ == "__main__":
    main()
