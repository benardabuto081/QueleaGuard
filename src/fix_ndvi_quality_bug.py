"""
Milestone 3.10 (bug fix) - Rebuild NDVI features for both presence and
pseudo-absence records, this time filtering to good-quality composites
BEFORE selecting the nearest prior composite (not just for the seasonal
baseline, which was already correctly filtered).

Root cause: MODIS fill value (-3000, "Pixel not produced due to other
reasons than clouds") was being selected as a valid nearest-composite
value in 8 of 266 records, affecting cells with unusually high
bad-quality composite rates (cell_0014, cell_0097, cell_0079).

Output: data/processed/ndvi_features.csv (presence, corrected)
        data/processed/ndvi_features_pseudo_absence.csv (pseudo-absence, corrected)
"""

import pandas as pd

ORIGINAL_NDVI = "data/external/appeears_ndvi_full_history.csv"
GAP_FILL_NDVI = "data/external/appeears_ndvi_pseudo_absence_gap.csv"
OCCURRENCES_PATH = "data/processed/occurrences_with_grid_cell.csv"
PSEUDO_ABSENCES_PATH = "data/processed/pseudo_absences_final.csv"

NDVI_COL = "MOD13Q1_061__250m_16_days_NDVI"
QUALITY_COL = "MOD13Q1_061__250m_16_days_VI_Quality_MODLAND_Description"


def compute_ndvi_features(records_df, key_col, date_col, ndvi_good, seasonal_baseline, output_path):
    results = []
    for _, row in records_df.iterrows():
        cell_id = row["grid_cell_id"]
        obs_date = row[date_col]

        cell_series = ndvi_good[ndvi_good["ID"] == cell_id].sort_values("Date")
        prior = cell_series[cell_series["Date"] <= obs_date]

        if prior.empty:
            nearest_ndvi, nearest_date, days_gap = None, None, None
        else:
            nearest_row = prior.iloc[-1]
            nearest_ndvi = nearest_row[NDVI_COL]
            nearest_date = nearest_row["Date"]
            days_gap = (obs_date - nearest_date).days

        month = obs_date.month
        baseline = seasonal_baseline.get((cell_id, month), None)
        anomaly = (nearest_ndvi - baseline) if (nearest_ndvi is not None and baseline is not None) else None

        results.append({
            "record_key": row[key_col],
            "grid_cell_id": cell_id,
            "observation_date": obs_date.date(),
            "ndvi_nearest_composite": round(nearest_ndvi, 4) if nearest_ndvi is not None else None,
            "ndvi_composite_date": nearest_date.date() if nearest_date is not None else None,
            "ndvi_days_gap": days_gap,
            "ndvi_seasonal_baseline": round(baseline, 4) if baseline is not None else None,
            "ndvi_anomaly": round(anomaly, 4) if anomaly is not None else None,
        })

    results_df = pd.DataFrame(results)
    results_df.to_csv(output_path, index=False)
    return results_df


def main():
    original = pd.read_csv(ORIGINAL_NDVI)
    gap_fill = pd.read_csv(GAP_FILL_NDVI)
    ndvi_all = pd.concat([original, gap_fill], ignore_index=True)
    ndvi_all["Date"] = pd.to_datetime(ndvi_all["Date"])

    # CRITICAL FIX: filter to good-quality composites BEFORE any selection,
    # not just for the baseline calculation.
    ndvi_good = ndvi_all[ndvi_all[QUALITY_COL] == "VI produced with good quality"].copy()
    print(f"Total composites: {len(ndvi_all)}, good-quality: {len(ndvi_good)} "
          f"({100*len(ndvi_good)/len(ndvi_all):.1f}%)")

    ndvi_good["month"] = ndvi_good["Date"].dt.month
    seasonal_baseline = ndvi_good.groupby(["ID", "month"])[NDVI_COL].mean()

    # --- Presence records ---
    occ = pd.read_csv(OCCURRENCES_PATH)
    occ["year"] = pd.to_numeric(occ["year"], errors="coerce")
    presences = occ[(occ["year"] >= 2000) & (occ["grid_cell_id"].notna())].copy()
    presences["eventDate_parsed"] = pd.to_datetime(presences["eventDate"].str[:10], format="%Y-%m-%d", errors="coerce")
    presences = presences.dropna(subset=["eventDate_parsed"])
    presences = presences.rename(columns={"key": "record_key_orig"})

    presence_results = compute_ndvi_features(
        presences.rename(columns={"record_key_orig": "key"}), "key", "eventDate_parsed",
        ndvi_good, seasonal_baseline, "data/processed/ndvi_features.csv"
    )
    print(f"\nPresence NDVI features recomputed: {len(presence_results)} records")
    print(f"Missing (no valid prior composite): {presence_results['ndvi_nearest_composite'].isna().sum()}")
    invalid = presence_results[(presence_results['ndvi_nearest_composite'] < -1) | (presence_results['ndvi_nearest_composite'] > 1)]
    print(f"Still out-of-range: {len(invalid)}")

    # --- Pseudo-absence records ---
    pa = pd.read_csv(PSEUDO_ABSENCES_PATH)
    pa["eventDate_parsed"] = pd.to_datetime(pa["eventDate"].astype(str).str[:10], format="%Y-%m-%d", errors="coerce")
    pa = pa.dropna(subset=["eventDate_parsed"])
    pa = pa.rename(columns={"key": "record_key_orig"})

    pa_results = compute_ndvi_features(
        pa.rename(columns={"record_key_orig": "key"}), "key", "eventDate_parsed",
        ndvi_good, seasonal_baseline, "data/processed/ndvi_features_pseudo_absence.csv"
    )
    print(f"\nPseudo-absence NDVI features recomputed: {len(pa_results)} records")
    print(f"Missing (no valid prior composite): {pa_results['ndvi_nearest_composite'].isna().sum()}")
    invalid_pa = pa_results[(pa_results['ndvi_nearest_composite'] < -1) | (pa_results['ndvi_nearest_composite'] > 1)]
    print(f"Still out-of-range: {len(invalid_pa)}")


if __name__ == "__main__":
    main()
