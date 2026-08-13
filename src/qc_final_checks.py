"""
Milestone 4.4 (QC, final) - Cross-class contradiction check and year
distribution comparison on the corrected pseudo-absence set, completing
the QC pass before any environmental feature extraction begins.
"""

import pandas as pd

OCCURRENCES_PATH = "data/processed/occurrences_with_grid_cell.csv"
PA_FINAL_PATH = "data/processed/pseudo_absences_final.csv"


def main():
    occ = pd.read_csv(OCCURRENCES_PATH)
    occ["year"] = pd.to_numeric(occ["year"], errors="coerce")
    presences = occ[(occ["year"] >= 2000) & (occ["grid_cell_id"].notna())].copy()
    presences["obs_date"] = pd.to_datetime(presences["eventDate"].astype(str).str[:10], format="%Y-%m-%d", errors="coerce").dt.date
    presences["presence"] = 1

    pa = pd.read_csv(PA_FINAL_PATH)
    pa["obs_date"] = pd.to_datetime(pa["eventDate"].astype(str).str[:10], format="%Y-%m-%d", errors="coerce").dt.date

    combined = pd.concat([
        presences[["grid_cell_id", "obs_date", "presence"]],
        pa[["grid_cell_id", "obs_date"]].assign(presence=0),
    ], ignore_index=True)

    print("=== CROSS-CLASS CONTRADICTION CHECK ===")
    cross = combined.groupby(["grid_cell_id", "obs_date"])["presence"].nunique()
    conflicts = cross[cross > 1]
    print(f"(cell, date) pairs with BOTH presence AND pseudo-absence: {len(conflicts)}")
    if len(conflicts) > 0:
        print(conflicts.to_string())
        print("*** SAFEGUARD FAILED - INVESTIGATE ***")
    else:
        print("Confirmed clean - the Log Entry 013 exclusion safeguard worked as designed.")

    print("\n=== YEAR DISTRIBUTION COMPARISON ===")
    pres_years = presences["year"].value_counts().sort_index()
    pa["year"] = pd.to_numeric(pa["year"], errors="coerce")
    pa_years = pa["year"].value_counts().sort_index()
    year_comp = pd.DataFrame({"presence": pres_years, "pseudo_absence": pa_years}).fillna(0).astype(int)
    print(year_comp.to_string())

    print("\n=== SPATIAL OVERLAP CHECK ===")
    print(f"Unique cells - presence: {presences['grid_cell_id'].nunique()}, pseudo-absence: {pa['grid_cell_id'].nunique()}")
    print(f"Cells used by both: {len(set(presences['grid_cell_id']) & set(pa['grid_cell_id']))}")


if __name__ == "__main__":
    main()
