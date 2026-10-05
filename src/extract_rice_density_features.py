"""
Level 2 - Rice-landscape density feature extraction (Log Entry 015).

For each point in modelling_dataset_final.csv, computes:
  - rice_pct_500m, rice_pct_1000m, rice_pct_2000m: pct of rice-classified
    pixels within circular buffers of that radius (Jiang et al. 2025 raster)
  - dist_to_nearest_rice_m: distance to the nearest rice pixel, via an
    expanding search window capped at 20km

Output: data/processed/rice_density_features.csv
"""

import math
import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import from_bounds

RASTER_PATH = "data/external/rice_raster/Kenya.tif"
INPUT_PATH = "data/processed/modelling_dataset_final.csv"
OUTPUT_PATH = "data/processed/rice_density_features.csv"

BUFFER_RADII_M = [500, 1000, 2000]
MAX_BUFFER_CHECK_M = max(BUFFER_RADII_M) + 100
DIST_SEARCH_STEPS_M = [2000, 5000, 10000, 20000]
M_PER_DEG_LAT = 111320.0


def deg_window(lat, lon, radius_m):
    dlat = radius_m / M_PER_DEG_LAT
    dlon = radius_m / (M_PER_DEG_LAT * math.cos(math.radians(lat)))
    return lon - dlon, lat - dlat, lon + dlon, lat + dlat


def read_window(src, lat, lon, radius_m):
    minx, miny, maxx, maxy = deg_window(lat, lon, radius_m)
    window = from_bounds(minx, miny, maxx, maxy, src.transform)
    data = src.read(1, window=window)
    transform = src.window_transform(window)
    return data, transform


def pixel_distances_m(transform, shape, lat, lon):
    rows, cols = np.indices(shape)
    xs, ys = rasterio.transform.xy(transform, rows.ravel(), cols.ravel())
    xs = np.array(xs).reshape(shape)
    ys = np.array(ys).reshape(shape)
    dx = (xs - lon) * M_PER_DEG_LAT * math.cos(math.radians(lat))
    dy = (ys - lat) * M_PER_DEG_LAT
    return np.sqrt(dx ** 2 + dy ** 2)


def compute_buffer_fractions(src, lat, lon):
    data, transform = read_window(src, lat, lon, MAX_BUFFER_CHECK_M)
    if data.size == 0:
        return {f"rice_pct_{r}m": np.nan for r in BUFFER_RADII_M}
    dist = pixel_distances_m(transform, data.shape, lat, lon)
    result = {}
    for r in BUFFER_RADII_M:
        within = dist <= r
        n = within.sum()
        result[f"rice_pct_{r}m"] = float((data[within] == 1).mean() * 100) if n > 0 else np.nan
    return result


def compute_distance_to_nearest_rice(src, lat, lon):
    for radius_m in DIST_SEARCH_STEPS_M:
        data, transform = read_window(src, lat, lon, radius_m)
        if data.size == 0:
            continue
        rice_mask = data == 1
        if not rice_mask.any():
            continue
        dist = pixel_distances_m(transform, data.shape, lat, lon)
        return float(dist[rice_mask].min()), radius_m
    return np.nan, DIST_SEARCH_STEPS_M[-1]


def main():
    points = pd.read_csv(INPUT_PATH)[["record_key", "latitude", "longitude"]]
    print(f"Processing {len(points)} points...")

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

    print("\nSummary:")
    for r in BUFFER_RADII_M:
        col = f"rice_pct_{r}m"
        print(f"  {col}: mean={out[col].mean():.2f}%, nulls={out[col].isna().sum()}")
    print(f"  dist_to_nearest_rice_m: mean={out['dist_to_nearest_rice_m'].mean():.1f}, "
          f"max={out['dist_to_nearest_rice_m'].max():.1f}, nulls={out['dist_to_nearest_rice_m'].isna().sum()}")
    expanded = int((out["dist_search_radius_used_m"] > DIST_SEARCH_STEPS_M[0]).sum())
    print(f"  Points requiring expanded search beyond {DIST_SEARCH_STEPS_M[0]}m: {expanded}")


if __name__ == "__main__":
    main()
