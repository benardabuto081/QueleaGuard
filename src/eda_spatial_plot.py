"""
Milestone 4.2 - EDA: spatial visualization. Plots the 328-cell analysis
grid (shaded by scheme-boundary membership), presence points, and
pseudo-absence points together, restricted to the 259 records actually
in the frozen modelling dataset (i.e., respecting all Phase 3 exclusions).

Output: reports/figures/spatial_distribution.png
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os

os.makedirs("reports/figures", exist_ok=True)

DATASET_PATH = "data/processed/modelling_dataset_final.csv"
OCCURRENCES_PATH = "data/processed/occurrences_with_grid_cell.csv"
PSEUDO_ABSENCES_PATH = "data/processed/pseudo_absences_final.csv"
GRID_PATH = "data/processed/analysis_grid.geojson"
OUTPUT_PATH = "reports/figures/spatial_distribution.png"


def main():
    final = pd.read_csv(DATASET_PATH)
    final_keys = set(final["record_key"])

    occ = pd.read_csv(OCCURRENCES_PATH).rename(columns={"key": "record_key"})
    occ = occ[occ["record_key"].isin(final_keys)]

    pa = pd.read_csv(PSEUDO_ABSENCES_PATH).rename(columns={"key": "record_key"})
    pa = pa[pa["record_key"].isin(final_keys)]

    print(f"Presence points to plot: {len(occ)}")
    print(f"Pseudo-absence points to plot: {len(pa)}")
    print(f"Total: {len(occ) + len(pa)} (should equal {len(final)})")

    grid = gpd.read_file(GRID_PATH)

    fig, ax = plt.subplots(figsize=(12, 12))

    grid[grid["within_scheme_boundary"] == False].plot(
        ax=ax, facecolor="none", edgecolor="lightgray", linewidth=0.4, zorder=1
    )
    grid[grid["within_scheme_boundary"] == True].plot(
        ax=ax, facecolor="gold", edgecolor="orange", alpha=0.3, linewidth=1.2, zorder=2
    )

    ax.scatter(
        pa["decimalLongitude"], pa["decimalLatitude"],
        c="steelblue", s=30, alpha=0.6, label=f"Pseudo-absence (n={len(pa)})", zorder=3
    )
    ax.scatter(
        occ["decimalLongitude"], occ["decimalLatitude"],
        c="crimson", s=30, alpha=0.7, label=f"Presence (n={len(occ)})", zorder=4
    )

    ax.set_title("QueleaGuard: Presence / Pseudo-Absence Spatial Distribution\n"
                  "(328-cell analysis grid, Ahero scheme boundary highlighted)")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend(loc="upper right")
    ax.set_aspect("equal")

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=150)
    print(f"\nSaved figure to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
