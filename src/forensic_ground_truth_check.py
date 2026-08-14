"""
Ground-truth reconciliation (read-only). Confirms/refutes the PA
provenance staleness hypothesis via direct key comparison, and lists
ALL AppEEARS tasks on this account directly from the API, to resolve
the confusion between two different NDVI task submissions
(queleaguard_ndvi_pa_v2_gap_45cells vs queleaguard_ndvi_final_gap_36cells)
without relying on any prior session's account of what happened.

Makes NO changes to any file, submits no new tasks.
"""

import getpass
import requests
import pandas as pd
import os
import subprocess
import datetime

APPEEARS_API = "https://appeears.earthdatacloud.nasa.gov/api"

print("=" * 70)
print("PART 1: PSEUDO-ABSENCE PROVENANCE CHECK")
print("=" * 70)

paths = {
    "current (v2) pseudo_absences_final.csv": "data/processed/pseudo_absences_final.csv",
    "v1 (month-skewed) backup": "data/processed/pseudo_absences_final_v1_month_skewed.csv",
    "modelling_dataset_final.csv": "data/processed/modelling_dataset_final.csv",
}
dfs = {}
for label, path in paths.items():
    try:
        dfs[label] = pd.read_csv(path)
        print(f"{label}: {len(dfs[label])} rows")
    except FileNotFoundError:
        print(f"{label}: FILE NOT FOUND")

if all(l in dfs for l in paths):
    final = dfs["modelling_dataset_final.csv"]
    final_pa_keys = set(final[final["presence"] == 0]["record_key"])
    current_pa_keys = set(dfs["current (v2) pseudo_absences_final.csv"]["key"])
    v1_pa_keys = set(dfs["v1 (month-skewed) backup"]["key"])

    print(f"\nPA keys in modelling_dataset_final.csv: {len(final_pa_keys)}")
    print(f"  -> found in CURRENT (v2) pseudo_absences_final.csv: {len(final_pa_keys & current_pa_keys)}")
    print(f"  -> found in v1 (month-skewed) backup: {len(final_pa_keys & v1_pa_keys)}")
    unexplained = final_pa_keys - current_pa_keys - v1_pa_keys
    print(f"  -> found in NEITHER (genuinely unexplained): {len(unexplained)}")
    if unexplained:
        print(f"     Unexplained keys: {sorted(unexplained)}")

print("\nGit commit history for these two files:")
for f in ["data/processed/modelling_dataset_final.csv", "data/processed/pseudo_absences_final.csv"]:
    result = subprocess.run(["git", "log", "-3", "--format=%h %ad %s", "--date=iso", "--", f],
                             capture_output=True, text=True)
    print(f"\n{f}:")
    print(result.stdout)

print("\n" + "=" * 70)
print("PART 2: APPEEARS TASK LIST (direct from API, ground truth)")
print("=" * 70)

username = input("Earthdata username: ")
password = getpass.getpass("Earthdata password (hidden as you type): ")
token = requests.post(f"{APPEEARS_API}/login", auth=(username, password), timeout=30).json()["token"]
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(f"{APPEEARS_API}/task", headers=headers, timeout=30)
tasks = response.json()

ndvi_tasks = [t for t in tasks if "ndvi" in t.get("task_name", "").lower() or "quelea" in t.get("task_name", "").lower()]
print(f"\nFound {len(ndvi_tasks)} QueleaGuard/NDVI-related tasks on this account:\n")
for t in sorted(ndvi_tasks, key=lambda x: x.get("created", "")):
    print(f"  Task ID:   {t.get('task_id')}")
    print(f"  Name:      {t.get('task_name')}")
    print(f"  Status:    {t.get('status')}")
    print(f"  Created:   {t.get('created')}")
    n_coords = len(t.get("params", {}).get("coordinates", [])) if "params" in t else "?"
    print(f"  Coords:    {n_coords}")
    print()
