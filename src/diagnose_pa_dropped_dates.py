"""
Diagnose the 2 pseudo-absence records dropped during rainfall extraction
(133 -> 131) due to unparseable eventDate after .str[:10] truncation.
"""

import pandas as pd

pa = pd.read_csv("data/processed/pseudo_absences_final.csv")
parsed = pd.to_datetime(pa["eventDate"].astype(str).str[:10], format="%Y-%m-%d", errors="coerce")
dropped = pa[parsed.isna()]

print(f"Records with unparseable date: {len(dropped)}")
print(dropped[["key", "grid_cell_id", "eventDate", "year"]].to_string(index=False))
