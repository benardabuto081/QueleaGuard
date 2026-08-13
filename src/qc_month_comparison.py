"""
Milestone 4.4 (QC, corrected) - Proper month/year distribution comparison
between the corrected pseudo-absence sample and presence records, using
date-only truncation (.str[:10]) before parsing - the same defensive
pattern already used elsewhere in the pipeline (assemble_final_dataset.py,
fix_ndvi_quality_bug.py) to handle GBIF's mixed timestamp formats. The
previous QC attempt used bare pd.to_datetime() on the full column, which
silently produced NaT for ~89% of records due to pandas' single-format
inference from the first value - a diagnostic-script bug, not a data bug.
"""

import pandas as pd

OCCURRENCES_PATH = "data/processed/occurrences_with_grid_cell.csv"
PA_FINAL_PATH = "data/processed/pseudo_absences_final.csv"
PA_POOL_PATH = "data/processed/pseudo_absence_pool.csv"


def month_year_table(df, date_col, year_filter=True):
    d = df.copy()
    if year_filter:
        d["year"] = pd.to_numeric(d["year"], errors="coerce")
        d = d[d["year"] >= 2000]
    d["_date"] = pd.to_datetime(d[date_col].astype(str).str[:10], format="%Y-%m-%d", errors="coerce")
    print(f"  Parsed: {d['_date'].notna().sum()} / {len(d)}")
    return d["_date"].dt.month.value_counts().sort_index()


def main():
    occ = pd.read_csv(OCCURRENCES_PATH)
    print("=== PRESENCE month distribution ===")
    pres_months = month_year_table(occ, "eventDate")
    print(pres_months.to_string())

    pa_final = pd.read_csv(PA_FINAL_PATH)
    print("\n=== FINAL PSEUDO-ABSENCE (n=133) month distribution ===")
    pa_months = month_year_table(pa_final, "eventDate", year_filter=False)
    print(pa_months.to_string())

    pa_pool = pd.read_csv(PA_POOL_PATH)
    print("\n=== CANDIDATE POOL (n=429) month distribution ===")
    pool_months = month_year_table(pa_pool, "eventDate", year_filter=False)
    print(pool_months.to_string())

    print("\n=== SIDE-BY-SIDE COMPARISON (% of class total per month) ===")
    pres_pct = (pres_months / pres_months.sum() * 100).round(1)
    pa_pct = (pa_months / pa_months.sum() * 100).round(1)
    comparison = pd.DataFrame({"presence_%": pres_pct, "pseudo_absence_%": pa_pct}).fillna(0.0)
    print(comparison.to_string())

    max_pa_month_pct = pa_pct.max()
    print(f"\nMax single-month concentration - presence: {pres_pct.max():.1f}%, pseudo-absence: {max_pa_month_pct:.1f}%")
    if max_pa_month_pct > 30:
        print("FLAG: pseudo-absence still shows concerning month concentration (>30% in one month).")
    else:
        print("OK: no severe single-month concentration remains.")


if __name__ == "__main__":
    main()
