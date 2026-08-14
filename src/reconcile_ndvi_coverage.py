"""
Ground-truth NDVI coverage reconciliation. Pulls the ACTUAL cell list for
every completed AppEEARS task directly from the API (not from hardcoded
script lists, which may themselves be stale), and compares against what
the restored, correct 133-row pseudo-absence set + presence records
actually require. Determines whether the 36-cell task is a legitimate
fill of a real gap, or was computed against bad/stale data.

Read-only against AppEEARS. Read-only against local files.
"""

import getpass
import requests
import pandas as pd

APPEEARS_API = "https://appeears.earthdatacloud.nasa.gov/api"

username = input("Earthdata username: ")
password = getpass.getpass("Earthdata password (hidden as you type): ")
token = requests.post(f"{APPEEARS_API}/login", auth=(username, password), timeout=30).json()["token"]
headers = {"Authorization": f"Bearer {token}"}

ALL_TASKS = {
    "full_history_20cells (presence)": "28801afb-d2dc-4c7f-b999-72f567a455bf",
    "pseudo_absence_gap_43cells (v1 PA)": "0889d6bb-d49a-44c5-9a41-239ee27bff4f",
    "pa_v2_gap_45cells (v2 PA, this session)": "be74e08a-bee5-4418-acd1-e024b3582f93",
    "final_gap_36cells (other session)": "c03fe58e-5be4-4fcc-a9c2-a1ac7b1e122d",
}

task_cells = {}
for name, task_id in ALL_TASKS.items():
    resp = requests.get(f"{APPEEARS_API}/task/{task_id}", headers=headers, timeout=30)
    detail = resp.json()
    coords = detail.get("params", {}).get("coordinates", [])
    cells = set(c["id"] for c in coords)
    task_cells[name] = cells
    print(f"{name}: {len(cells)} cells")

all_covered = set().union(*task_cells.values())
print(f"\nTotal unique cells covered across ALL 4 tasks: {len(all_covered)}")

print("\n=== ACTUAL REQUIRED CELLS (from restored, correct local data) ===")
pa = pd.read_csv("data/processed/pseudo_absences_final.csv")
pa_cells = set(pa["grid_cell_id"].unique())
print(f"Pseudo-absence (v2, restored 133 rows) unique cells: {len(pa_cells)}")

occ = pd.read_csv("data/processed/occurrences_with_grid_cell.csv")
occ["year"] = pd.to_numeric(occ["year"], errors="coerce")
presence_cells = set(occ[occ["year"] >= 2000]["grid_cell_id"].dropna().unique())
print(f"Presence unique cells: {len(presence_cells)}")

truly_needed = pa_cells | presence_cells
print(f"Total cells actually needed (presence + v2 PA): {len(truly_needed)}")

still_missing = truly_needed - all_covered
print(f"\n=== TRUE REMAINING GAP (needed but not covered by any task) ===")
print(f"Count: {len(still_missing)}")
print(sorted(still_missing))

print(f"\n=== Does the 36-cell task cover any of the true gap? ===")
overlap_with_gap = task_cells["final_gap_36cells (other session)"] & truly_needed
print(f"36-cell task cells that are actually needed: {len(overlap_with_gap)}")
print(sorted(overlap_with_gap))
unneeded = task_cells["final_gap_36cells (other session)"] - truly_needed
print(f"36-cell task cells that are NOT needed (wasted/irrelevant): {len(unneeded)}")
print(sorted(unneeded))
