"""
Emergency restore + task coordinate verification (read-only on AppEEARS,
restore-only on the local file - no new submissions, no deletions of
task history).
"""

import subprocess
import getpass
import requests
import pandas as pd

APPEEARS_API = "https://appeears.earthdatacloud.nasa.gov/api"

print("=== STEP 1: Restore pseudo_absences_final.csv from last commit ===")
result = subprocess.run(
    ["git", "diff", "--stat", "HEAD", "--", "data/processed/pseudo_absences_final.csv"],
    capture_output=True, text=True
)
print("Diff vs HEAD before restore:")
print(result.stdout if result.stdout else "(no diff shown)")

restore = subprocess.run(
    ["git", "checkout", "HEAD", "--", "data/processed/pseudo_absences_final.csv"],
    capture_output=True, text=True
)
print(restore.stdout, restore.stderr)

df = pd.read_csv("data/processed/pseudo_absences_final.csv")
print(f"Restored file row count: {len(df)} (should be 133)")

print("\n=== STEP 2: Fetch full coordinate lists for both NDVI tasks ===")
username = input("Earthdata username: ")
password = getpass.getpass("Earthdata password (hidden as you type): ")
token = requests.post(f"{APPEEARS_API}/login", auth=(username, password), timeout=30).json()["token"]
headers = {"Authorization": f"Bearer {token}"}

task_ids = {
    "queleaguard_ndvi_pa_v2_gap_45cells": "be74e08a-bee5-4418-acd1-e024b3582f93",
    "queleaguard_ndvi_final_gap_36cells": "c03fe58e-5be4-4fcc-a9c2-a1ac7b1e122d",
}

task_cells = {}
for name, task_id in task_ids.items():
    resp = requests.get(f"{APPEEARS_API}/task/{task_id}", headers=headers, timeout=30)
    detail = resp.json()
    coords = detail.get("params", {}).get("coordinates", [])
    cell_ids = sorted([c["id"] for c in coords])
    task_cells[name] = set(cell_ids)
    print(f"\n{name} ({task_id}):")
    print(f"  Coordinate count: {len(coords)}")
    print(f"  Cell IDs: {cell_ids}")

print("\n=== STEP 3: Compare against our verified NEW_CELLS list (45 cells) ===")
EXPECTED_45 = {'cell_0000', 'cell_0011', 'cell_0020', 'cell_0033', 'cell_0039', 'cell_0046',
               'cell_0047', 'cell_0053', 'cell_0057', 'cell_0065', 'cell_0072', 'cell_0081',
               'cell_0101', 'cell_0106', 'cell_0107', 'cell_0119', 'cell_0124', 'cell_0126',
               'cell_0130', 'cell_0137', 'cell_0141', 'cell_0160', 'cell_0175', 'cell_0181',
               'cell_0182', 'cell_0184', 'cell_0194', 'cell_0199', 'cell_0201', 'cell_0203',
               'cell_0205', 'cell_0216', 'cell_0223', 'cell_0240', 'cell_0241', 'cell_0242',
               'cell_0243', 'cell_0251', 'cell_0253', 'cell_0260', 'cell_0265', 'cell_0278',
               'cell_0279', 'cell_0289', 'cell_0297'}

for name, cells in task_cells.items():
    print(f"\n{name}: matches expected 45-cell list? {cells == EXPECTED_45}")
    print(f"  In task but not expected: {sorted(cells - EXPECTED_45)}")
    print(f"  In expected but not task: {sorted(EXPECTED_45 - cells)}")
