"""
Milestone 4.3 - EDA: temporal/seasonal distribution. Checks month-of-year
and year distribution for presence vs pseudo-absence, to see whether the
rainfall-driven breeding-season hypothesis (Cheke et al. 2007, Log Entry
006) is visible in the raw observation dates.

Output: reports/figures/temporal_distribution.png
        reports/milestone_4_3_temporal_summary.txt
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

os.makedirs("reports/figures", exist_ok=True)

DATASET_PATH = "data/processed/modelling_dataset_final.csv"
SUMMARY_PATH = "reports/milestone_4_3_temporal_summary.txt"
OUTPUT_PATH = "reports/figures/temporal_distribution.png"

lines = []
def log(msg=""):
    print(msg)
    lines.append(str(msg))


def main():
    df = pd.read_csv(DATASET_PATH)
    df["observation_date"] = pd.to_datetime(df["observation_date"])
    df["month"] = df["observation_date"].dt.month
    df["year"] = df["observation_date"].dt.year

    log("=== MONTH DISTRIBUTION (presence vs pseudo-absence) ===")
    month_table = pd.crosstab(df["month"], df["presence"])
    month_table.columns = ["pseudo_absence", "presence"]
    log(month_table.to_string())

    log("\n=== YEAR DISTRIBUTION (presence vs pseudo-absence) ===")
    year_table = pd.crosstab(df["year"], df["presence"])
    year_table.columns = ["pseudo_absence", "presence"]
    log(year_table.to_string())

    log("\n=== PRESENCE MONTH CONCENTRATION ===")
    pres_months = df[df["presence"] == 1]["month"].value_counts().sort_index()
    log(f"Top 3 months for presence: {pres_months.sort_values(ascending=False).head(3).to_dict()}")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    month_table.plot(kind="bar", ax=axes[0], color=["steelblue", "crimson"])
    axes[0].set_title("Records by Month")
    axes[0].set_xlabel("Month")
    axes[0].set_ylabel("Count")
    axes[0].legend(["Pseudo-absence", "Presence"])

    year_table.plot(kind="bar", ax=axes[1], color=["steelblue", "crimson"], stacked=True)
    axes[1].set_title("Records by Year")
    axes[1].set_xlabel("Year")
    axes[1].set_ylabel("Count")
    axes[1].legend(["Pseudo-absence", "Presence"])

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=150)
    print(f"\nSaved figure to {OUTPUT_PATH}")

    with open(SUMMARY_PATH, "w") as f:
        f.write("\n".join(lines))
    print(f"Saved summary to {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
