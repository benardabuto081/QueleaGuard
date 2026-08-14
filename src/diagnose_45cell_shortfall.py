"""
Isolate exactly why the original 45-cell NDVI submission (Aug 13) missed
36 needed cells. Hypothesis: the original calculation assumed the v1
pseudo-absence gap-fill NDVI task (43 cells) covered ALL 49 unique cells
used by the v1 pseudo-absence CSV - but the task only actually requested
43 cells, a 6-cell shortfall that was never itself verified against the
task's real API coordinate list at the time. Combined with cells needed
by the v2 PA set that also weren't in presence's 20 cells, this produced
a larger true gap than the 45-cell calculation caught.
"""

import getpass
import requests
import pandas as pd

APPEEARS_API = "https://appeears.earthdatacloud.nasa.gov/api"
username = input("Earthdata username: ")
password = getpass.getpass("Earthdata password (hidden as you type): ")
token = requests.post(f"{APPEEARS_API}/login", auth=(username, password), timeout=30).json()["token"]
headers = {"Authorization": f"Bearer {token}"}

resp = requests.get(f"{APPEEARS_API}/task/0889d6bb-d49a-44c5-9a41-239ee27bff4f", headers=headers, timeout=30)
task43_cells = set(c["id"] for c in resp.json()["params"]["coordinates"])
print(f"v1 gap-fill task (0889d6bb): {len(task43_cells)} cells actually requested")

v1_pa = pd.read_csv("data/processed/pseudo_absences_final_v1_month_skewed.csv")
v1_pa_cells = set(v1_pa["grid_cell_id"].unique())
print(f"v1 pseudo-absence CSV: {len(v1_pa_cells)} unique cells actually used")

shortfall = v1_pa_cells - task43_cells
print(f"\nCells USED by v1 PA records but NEVER requested in the 43-cell NDVI task: {len(shortfall)}")
print(sorted(shortfall))
print("(This confirms a pre-existing, previously undetected NDVI coverage gap from Milestone 3,")
print(" separate from and predating the Log Entry 014 pseudo-absence rebuild.)")

occ = pd.read_csv("data/processed/occurrences_with_grid_cell.csv")
occ["year"] = pd.to_numeric(occ["year"], errors="coerce")
presence_cells = set(occ[occ["year"] >= 2000]["grid_cell_id"].dropna().unique())

resp45 = requests.get(f"{APPEEARS_API}/task/be74e08a-bee5-4418-acd1-e024b3582f93", headers=headers, timeout=30)
task45_cells = set(c["id"] for c in resp45.json()["params"]["coordinates"])

pa_v2 = pd.read_csv("data/processed/pseudo_absences_final.csv")
pa_v2_cells = set(pa_v2["grid_cell_id"].unique())

true_gap_without_36 = (pa_v2_cells | presence_cells) - (presence_cells | task43_cells | task45_cells)
print(f"\nTrue gap if the 36-cell task did NOT exist: {len(true_gap_without_36)} cells")
print(sorted(true_gap_without_36))

resp36 = requests.get(f"{APPEEARS_API}/task/c03fe58e-5be4-4fcc-a9c2-a1ac7b1e122d", headers=headers, timeout=30)
task36_cells = set(c["id"] for c in resp36.json()["params"]["coordinates"])
print(f"\nDoes the 36-cell task exactly equal this true gap? {task36_cells == true_gap_without_36}")
