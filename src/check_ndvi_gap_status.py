import getpass
import requests

APPEEARS_API = "https://appeears.earthdatacloud.nasa.gov/api"
TASK_ID = "0889d6bb-d49a-44c5-9a41-239ee27bff4f"

username = input("Earthdata username: ")
password = getpass.getpass("Earthdata password (hidden as you type): ")
token = requests.post(f"{APPEEARS_API}/login", auth=(username, password), timeout=30).json()["token"]

headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{APPEEARS_API}/task/{TASK_ID}", headers=headers, timeout=30)
data = response.json()
print(f"Status: {data.get('status')}")
