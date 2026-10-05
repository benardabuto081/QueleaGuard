"""
Generate a spatially random sample within the analysis extent, for the
Section 8 pseudo-absence representativeness check (presence vs pseudo-
absence vs spatially random, on rice-cover distribution).

Uses the same 50km buffer bounding box as the rice raster clip, and
samples uniformly at random (not effort-weighted) - deliberately
different from how the pseudo-absence pool was constructed.

Output: data/processed/spatial_random_sample.csv
"""

import numpy as np
import pandas as pd

MINX, MAXX = 34.40, 35.47
MINY, MAXY = -0.62, 0.29
N_SAMPLES = 266  # match presence+pseudo-absence count for a fair comparison
SEED = 42

np.random.seed(SEED)


def main():
    lons = np.random.uniform(MINX, MAXX, N_SAMPLES)
    lats = np.random.uniform(MINY, MAXY, N_SAMPLES)
    df = pd.DataFrame({
        "record_key": [f"random_{i:04d}" for i in range(N_SAMPLES)],
        "latitude": lats,
        "longitude": lons,
    })
    df.to_csv("data/processed/spatial_random_sample.csv", index=False)
    print(f"Saved {N_SAMPLES} spatially random points to data/processed/spatial_random_sample.csv")
    print(f"Lat range: {lats.min():.4f} to {lats.max():.4f}")
    print(f"Lon range: {lons.min():.4f} to {lons.max():.4f}")


if __name__ == "__main__":
    main()
