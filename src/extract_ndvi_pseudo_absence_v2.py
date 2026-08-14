"""
Milestone 4.5 (Stage 3) - QC-hardened NDVI extraction for the corrected
(v2, 133-record) pseudo-absence set. Combines all three raw NDVI sources
(presence 20-cell, v1 gap-fill 43-cell, v2 gap-fill 45-cell) - together
covering all 93 cells the current dataset actually needs, per the
reconciliation performed this session.

QC guarantees enforced by design, not discovered after the fact:
1. Quality filter (MODIS fill values, e.g. -3000) applied BEFORE nearest-
   composite selection - the exact bug class fixed in Task 190, built in
   from the start this time rather than retrofitted.
2. Every one of the 133 pseudo-absence records is accounted for in the
   output, including any with no valid prior composite (explicit reason
   given, never silently dropped or interpolated).
3. Explicit range validation (-1 to 1) with a hard assertion - fails
   loudly rather than proceeding if a bad value gets through.
4. Raw source files are read, never modified. A combined-source snapshot
   is saved separately for reproducibility.
5. Nothing here touches modelling_dataset_final.csv - extraction only.

Output: data/processed/ndvi_features_pseudo_absence.csv
        data/external/appeears_ndvi_combined_sources_snapshot.csv
        reports/milestone_4_5_ndvi_extraction_qc_report.txt
"""

import pandas as pd

SOURCES = [
    "data/external/appeears_ndvi_full_history.csv",
    "data/external/appeears_ndvi_pseudo_absence_gap.csv",
    "data/external/appeears_ndvi_pa_v2_gap_45cells.csv",
]
PA_PATH = "data/processed/pseudo_absences_final.csv"
NDVI_COL = "MOD13Q1_061__250m_16_days_NDVI"
QUALITY_COL = "MOD13Q1_061__250m_16_days_VI_Quality_MODLAND_Description"
GOOD_QUALITY_LABEL = "VI produced with good quality"

OUTPUT_PATH = "data/processed/ndvi_features_pseudo_absence.csv"
SNAPSHOT_PATH = "data/external/appeears_ndvi_combined_sources_snapshot.csv"
QC_REPORT_PATH = "reports/milestone_4_5_ndvi_extraction_qc_report.txt"

qc_lines = []
def log(msg=""):
    print(msg)
    qc_lines.append(str(msg))


def main():
    log("=== MILESTONE 4.5 NDVI EXTRACTION QC REPORT ===\n")

    # --- Load and combine raw sources (read-only) ---
    frames = []
    for path in SOURCES:
        df = pd.read_csv(path)
        df["_source_file"] = path
        frames.append(df)
        log(f"Loaded {path}: {len(df)} rows, {df['ID'].nunique()} unique cells")
    combined = pd.concat(frames, ignore_index=True)
    combined["Date"] = pd.to_datetime(combined["Date"])
    combined.to_csv(SNAPSHOT_PATH, index=False)
    log(f"\nCombined raw catalog: {len(combined)} rows, {combined['ID'].nunique()} unique cells")
    log(f"Snapshot saved to {SNAPSHOT_PATH} (raw sources untouched)")

    # --- Quality filter applied BEFORE any selection logic ---
    good = combined[combined[QUALITY_COL] == GOOD_QUALITY_LABEL].copy()
    log(f"\nGood-quality composites: {len(good)} / {len(combined)} "
        f"({100*len(good)/len(combined):.1f}%)")

    # Explicit fill-value check (belt and suspenders on top of the quality label filter)
    fill_value_check = combined[combined[NDVI_COL] <= -3000]
    log(f"Records with MODIS fill value (-3000) in raw data: {len(fill_value_check)} "
        f"(all must be excluded by the quality filter above - verifying...)")
    fill_in_good = good[good[NDVI_COL] <= -3000]
    assert len(fill_in_good) == 0, f"FATAL: {len(fill_in_good)} fill-value records leaked through the quality filter"
    log("Confirmed: zero fill-value records present in the good-quality subset.")

    good["month"] = good["Date"].dt.month
    seasonal_baseline = good.groupby(["ID", "month"])[NDVI_COL].mean()

    # --- Load corrected pseudo-absence records ---
    pa = pd.read_csv(PA_PATH)
    log(f"\nPseudo-absence records to process: {len(pa)} (expected 133)")
    assert len(pa) == 133, f"FATAL: expected 133 pseudo-absence records, found {len(pa)} - check pseudo_absences_final.csv integrity before proceeding"

    pa = pa.rename(columns={"key": "record_key"})
    pa["obs_date"] = pd.to_datetime(pa["eventDate"].astype(str).str[:10], format="%Y-%m-%d", errors="coerce")
    date_parse_failures = pa[pa["obs_date"].isna()]
    log(f"Date parsing failures: {len(date_parse_failures)}")
    if len(date_parse_failures) > 0:
        log(date_parse_failures[["record_key", "grid_cell_id", "eventDate"]].to_string(index=False))

    # --- Cell coverage check before extraction ---
    needed_cells = set(pa["grid_cell_id"].unique())
    covered_cells = set(good["ID"].unique())
    uncovered = needed_cells - covered_cells
    log(f"\nGrid cells needed: {len(needed_cells)}")
    log(f"Grid cells with NDVI data available: {len(needed_cells & covered_cells)} / {len(needed_cells)}")
    if uncovered:
        log(f"WARNING - cells needed but with NO NDVI data at all: {sorted(uncovered)}")

    # --- Per-record extraction with explicit accounting ---
    results = []
    accounting = {"success": 0, "missing_no_prior_composite": 0, "missing_no_cell_coverage": 0, "date_parse_failure": 0}

    for _, row in pa.iterrows():
        record_key = row["record_key"]
        cell_id = row["grid_cell_id"]
        obs_date = row["obs_date"]

        if pd.isna(obs_date):
            accounting["date_parse_failure"] += 1
            results.append({
                "record_key": record_key, "grid_cell_id": cell_id, "observation_date": None,
                "ndvi_nearest_composite": None, "ndvi_composite_date": None, "ndvi_days_gap": None,
                "ndvi_seasonal_baseline": None, "ndvi_anomaly": None,
                "extraction_status": "FAILED_DATE_PARSE",
            })
            continue

        if cell_id not in covered_cells:
            accounting["missing_no_cell_coverage"] += 1
            results.append({
                "record_key": record_key, "grid_cell_id": cell_id, "observation_date": obs_date.date(),
                "ndvi_nearest_composite": None, "ndvi_composite_date": None, "ndvi_days_gap": None,
                "ndvi_seasonal_baseline": None, "ndvi_anomaly": None,
                "extraction_status": "MISSING_NO_CELL_COVERAGE",
            })
            continue

        cell_series = good[good["ID"] == cell_id].sort_values("Date")
        prior = cell_series[cell_series["Date"] <= obs_date]

        if prior.empty:
            accounting["missing_no_prior_composite"] += 1
            results.append({
                "record_key": record_key, "grid_cell_id": cell_id, "observation_date": obs_date.date(),
                "ndvi_nearest_composite": None, "ndvi_composite_date": None, "ndvi_days_gap": None,
                "ndvi_seasonal_baseline": None, "ndvi_anomaly": None,
                "extraction_status": "MISSING_NO_PRIOR_COMPOSITE",
            })
            continue

        nearest_row = prior.iloc[-1]
        nearest_ndvi = nearest_row[NDVI_COL]
        nearest_date = nearest_row["Date"]
        days_gap = (obs_date - nearest_date).days

        baseline = seasonal_baseline.get((cell_id, obs_date.month), None)
        anomaly = (nearest_ndvi - baseline) if baseline is not None else None

        accounting["success"] += 1
        results.append({
            "record_key": record_key, "grid_cell_id": cell_id, "observation_date": obs_date.date(),
            "ndvi_nearest_composite": round(nearest_ndvi, 4),
            "ndvi_composite_date": nearest_date.date(),
            "ndvi_days_gap": days_gap,
            "ndvi_seasonal_baseline": round(baseline, 4) if baseline is not None else None,
            "ndvi_anomaly": round(anomaly, 4) if (baseline is not None) else None,
            "extraction_status": "SUCCESS",
        })

    results_df = pd.DataFrame(results)

    log(f"\n=== EXTRACTION ACCOUNTING (all 133 records) ===")
    for status, count in accounting.items():
        log(f"  {status}: {count}")
    total_accounted = sum(accounting.values())
    log(f"  TOTAL ACCOUNTED: {total_accounted} (must equal 133: {total_accounted == 133})")
    assert total_accounted == 133, "FATAL: record accounting does not sum to 133 - some record was neither succeeded nor explicitly logged as missing"

    # --- Range validation on successful extractions ---
    successful = results_df[results_df["extraction_status"] == "SUCCESS"]
    out_of_range = successful[(successful["ndvi_nearest_composite"] < -1) | (successful["ndvi_nearest_composite"] > 1)]
    log(f"\n=== RANGE VALIDATION ===")
    log(f"Successful extractions: {len(successful)}")
    log(f"Out-of-range values (outside -1 to 1): {len(out_of_range)}")
    assert len(out_of_range) == 0, f"FATAL: {len(out_of_range)} out-of-range NDVI values in successful extractions - do not proceed"
    if len(successful) > 0:
        log(f"Valid range observed: {successful['ndvi_nearest_composite'].min():.4f} to {successful['ndvi_nearest_composite'].max():.4f}")

    results_df.to_csv(OUTPUT_PATH, index=False)
    log(f"\nSaved to {OUTPUT_PATH}")
    log(f"\n*** This file has {len(results_df)} rows (all 133 pseudo-absence records, including any")
    log(f"    marked MISSING - nothing was dropped or silently imputed). Downstream assembly must")
    log(f"    explicitly decide how to handle non-SUCCESS rows before this enters the modelling")
    log(f"    dataset, not treat this file as already model-ready. ***")

    with open(QC_REPORT_PATH, "w") as f:
        f.write("\n".join(qc_lines))
    print(f"\nQC report saved to {QC_REPORT_PATH}")


if __name__ == "__main__":
    main()
