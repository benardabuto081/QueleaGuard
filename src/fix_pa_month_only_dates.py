"""
Apply the Log Entry 011 precedent (month-only-precision date -> day-01
placeholder) to the 2 records found with this issue in the rebuilt
pseudo-absence set. Fixed at the source in pseudo_absences_final.csv so
all downstream extraction scripts (rainfall, meteorology, NDVI) handle
these records consistently instead of each silently dropping them.
"""

import pandas as pd

PATH = "data/processed/pseudo_absences_final.csv"

df = pd.read_csv(PATH)
mask = df["eventDate"].astype(str).str.match(r"^\d{4}-\d{2}$")
affected = df[mask]
print(f"Records with month-only precision: {len(affected)}")
print(affected[["key", "grid_cell_id", "eventDate"]].to_string(index=False))

df.loc[mask, "eventDate"] = df.loc[mask, "eventDate"].astype(str) + "-01"

df.to_csv(PATH, index=False)
print(f"\nFixed. New eventDate values:")
print(df[mask][["key", "grid_cell_id", "eventDate"]].to_string(index=False))
