"""
Fix - assign day-01 to the 2 pseudo-absence records with month-only
precision dates, documented explicitly rather than silently dropped.
"""

import pandas as pd

pa = pd.read_csv("data/processed/pseudo_absences_final.csv")
mask = pa["eventDate"].astype(str).str.match(r"^\d{4}-\d{2}$")
print(f"Records with month-only dates: {mask.sum()}")
print(pa[mask][["key", "eventDate"]])

pa.loc[mask, "eventDate"] = pa.loc[mask, "eventDate"] + "-01"
print("\nFixed dates:")
print(pa[mask][["key", "eventDate"]])

pa.to_csv("data/processed/pseudo_absences_final.csv", index=False)
print("\nSaved updated pseudo_absences_final.csv")
