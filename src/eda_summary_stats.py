"""
Milestone 4.1 - EDA: descriptive statistics, class-conditional distributions,
correlation matrix, and outlier flagging on the frozen 259-record modelling
dataset.

Output: reports/milestone_4_1_eda_summary_stats.txt
"""

import pandas as pd
import numpy as np

DATASET_PATH = "data/processed/modelling_dataset_final.csv"
SUMMARY_PATH = "reports/milestone_4_1_eda_summary_stats.txt"

FEATURE_COLS = [
    "rainfall_7d", "rainfall_30d", "rainfall_90d",
    "temp_mean_7d", "dewpoint_mean_7d", "wind_mean_7d",
    "temp_same_day", "dewpoint_same_day", "wind_same_day",
    "ndvi_nearest_composite", "ndvi_anomaly",
    "elevation_m", "slope_deg", "dist_to_water_m",
]

lines = []
def log(msg=""):
    print(msg)
    lines.append(str(msg))


def main():
    df = pd.read_csv(DATASET_PATH)

    log("=== DATASET SHAPE ===")
    log(f"{len(df)} records, {len(df.columns)} columns")
    log(f"Class balance: {dict(df['presence'].value_counts())}")

    log("\n=== DESCRIPTIVE STATISTICS (full dataset) ===")
    log(df[FEATURE_COLS].describe().T.to_string())

    log("\n=== CLASS-CONDITIONAL MEANS (presence=1 vs presence=0) ===")
    grouped = df.groupby("presence")[FEATURE_COLS].mean().T
    grouped.columns = ["pseudo_absence (0)", "presence (1)"]
    grouped["difference"] = grouped["presence (1)"] - grouped["pseudo_absence (0)"]
    log(grouped.to_string())

    log("\n=== CLASS-CONDITIONAL MEDIANS ===")
    grouped_med = df.groupby("presence")[FEATURE_COLS].median().T
    grouped_med.columns = ["pseudo_absence (0)", "presence (1)"]
    log(grouped_med.to_string())

    log("\n=== CORRELATION MATRIX (feature-to-feature, Pearson) ===")
    corr = df[FEATURE_COLS].corr()
    log(corr.round(2).to_string())

    log("\n=== HIGH FEATURE-FEATURE CORRELATIONS (|r| > 0.7, excluding diagonal) ===")
    high_corr = []
    for i in range(len(FEATURE_COLS)):
        for j in range(i + 1, len(FEATURE_COLS)):
            r = corr.iloc[i, j]
            if abs(r) > 0.7:
                high_corr.append((FEATURE_COLS[i], FEATURE_COLS[j], round(r, 3)))
    if high_corr:
        for a, b, r in high_corr:
            log(f"  {a} <-> {b}: r={r}")
    else:
        log("  None found.")

    log("\n=== FEATURE-TARGET CORRELATION (point-biserial, feature vs presence) ===")
    target_corr = df[FEATURE_COLS + ["presence"]].corr()["presence"].drop("presence").sort_values(key=abs, ascending=False)
    log(target_corr.round(3).to_string())

    log("\n=== OUTLIER FLAGGING (IQR method, 1.5x fence) ===")
    for col in FEATURE_COLS:
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        outliers = df[(df[col] < lo) | (df[col] > hi)]
        if len(outliers) > 0:
            log(f"  {col}: {len(outliers)} outlier(s), fence=({lo:.2f}, {hi:.2f}), "
                f"values={sorted(outliers[col].tolist())}")

    log("\n=== WITHIN-SCHEME-BOUNDARY BREAKDOWN ===")
    log(df.groupby(["record_type", "within_scheme_boundary"]).size().to_string())

    with open(SUMMARY_PATH, "w") as f:
        f.write("\n".join(lines))
    print(f"\nSaved to {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
