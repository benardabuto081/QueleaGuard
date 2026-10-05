"""
Run the same rice-density extraction logic (Log Entry 015) against the
spatially random sample, for the Section 8 pseudo-absence representativeness
check.
"""

import pandas as pd
import rasterio
import sys

sys.path.insert(0, "src")
from extract_rice_density_features import (
    RASTER_PATH, BUFFER_RADII_M, DIST_SEARCH_STEPS_M,
    compute_buffer_fractions, compute_distance_to_nearest_rice,
)

INPUT_PATH = "data/processed/spatial_random_sample.csv"
OUTPUT_PATH = "data/processed/rice_density_features_random_sample.csv"


def main():
    points = pd.read_csv(INPUT_PATH)[["record_key", "latitude", "longitude"]]
    print(f"Processing {len(points)} random points...")

    results = []
    with rasterio.open(RASTER_PATH) as src:
        for i, row in points.iterrows():
            fractions = compute_buffer_fractions(src, row["latitude"], row["longitude"])
            dist_m, search_radius = compute_distance_to_nearest_rice(src, row["latitude"], row["longitude"])
            results.append({
                "record_key": row["record_key"],
                **fractions,
                "dist_to_nearest_rice_m": dist_m,
                "dist_search_radius_used_m": search_radius,
            })
            if (i + 1) % 50 == 0:
                print(f"  {i + 1}/{len(points)} done")

    out = pd.DataFrame(results)
    out.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
