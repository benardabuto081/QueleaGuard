import pandas as pd
pa = pd.read_csv("data/processed/pseudo_absences_final.csv")
pa["parsed"] = pd.to_datetime(pa["eventDate"].astype(str).str[:10], format="%Y-%m-%d", errors="coerce")
print(f"Total: {len(pa)}, failed to parse: {pa['parsed'].isna().sum()}")
print(pa[pa["parsed"].isna()][["key", "eventDate", "grid_cell_id"]])
