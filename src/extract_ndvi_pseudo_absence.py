"""
Milestone 3.9/3.10 (final) - Compute NDVI features for the 133
pseudo-absence records, combining the original 20-cell time series
(Milestone 3.6) with the newly-downloaded 43-cell gap-fill (this task),
so all 63 grid cells used across presence + pseudo-absence records have
NDVI coverage.

Output: data/processed/ndvi_features_pseudo_absence.csv
"""

import pandas as pd

ORIGINAL_NDVI = "data/external/appeears_ndvi_full_history.csv"
GAP_FILL_NDVI = "data/external/appeears_ndvi_pseudo_absence_gap.csv"
PSEUDO_ABSENCES_PATH = "data/processed/pseudo_absences_final.csv"
OUTPUT_PATH = "data/processed/ndvi_features_pseudo_absence.csv"

NDVI_COL = "MOD13Q1_061__250m_16_days_NDVI"
QUALITY_COL = "MOD13Q1_061__250m_16_days_VI_Quality_MODLAND_Description"


def main():
    original = pd.read_csv(ORIGINAL_NDVI)
    gap_fill = pd.read_csv(GAP_FILL_NDVI)

    combined = pd.concat([original, gap_fill], ignore_index=True)
    combined["Date"] = pd.to_datetime(combined["Date"])
    print(f"Combined NDVI time series: {len(combined)} rows, {combined['ID'].nunique()} unique cells")

    good_quality = combined[combined[QUALITY_COL] == "VI produced with good quality"].copy()
    good_quality["month"] = good_quality["Date"].dt.month
    seasonal_baseline = good_quality.groupby(["ID", "month"])[NDVI_COL].mean()

    pa = pd.read_csv(PSEUDO_ABSENCES_PATH)
    pa["eventDate_parsed"] = pd.to_datetime(pa["eventDate"].astype(str).str[:10], format="%Y-%m-%d", errors="coerce")
    pa = pa.dropna(subset=["eventDate_parsed"])
    print(f"Pseudo-absence records to process: {len(pa)}")

    results = []
    for _, row in pa.iterrows():
        cell_id = row["grid_cell_id"]
        obs_date = row["eventDate_parsed"]

        cell_series = combined[combined["ID"] == cell_id].sort_values("Date")
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
            "record_key": row["key"],
            "grid_cell_id": cell_id,
            "observation_date": obs_date.date(),
            "ndvi_nearest_composite": round(nearest_ndvi, 4) if nearest_ndvi is not None else None,
            "ndvi_composite_date": nearest_date.date() if nearest_date is not None else None,
            "ndvi_days_gap": days_gap,
            "ndvi_seasonal_baseline": round(baseline, 4) if baseline is not None else None,
            "ndvi_anomaly": round(anomaly, 4) if anomaly is not None else None,
        })

    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nExtracted NDVI features for {len(results_df)} pseudo-absence records.")
    print(f"Missing NDVI (no prior composite found): {results_df['ndvi_nearest_composite'].isna().sum()}")
    print(f"Saved to {OUTPUT_PATH}")
    print("\nSample results:")
    print(results_df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
