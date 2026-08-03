"""
Milestone 3.7 (final) - Extract elevation and compute slope for every
grid cell in the analysis extent, from the merged SRTM mosaic.

Slope computed via standard gradient method (Horn's algorithm, as
implemented in numpy.gradient on the elevation array), in degrees.

Output: data/processed/terrain_features.csv
        reports/milestone_3_7_terrain_extraction_summary.txt
"""

import numpy as np
import rasterio
import geopandas as gpd

MOSAIC_PATH = "data/external/srtm_mosaic.tif"
GRID_PATH = "data/processed/analysis_grid.geojson"
OUTPUT_PATH = "data/processed/terrain_features.csv"
SUMMARY_PATH = "reports/milestone_3_7_terrain_extraction_summary.txt"
UTM_CRS = "EPSG:32736"
WGS84_CRS = "EPSG:4326"


def main():
    grid = gpd.read_file(GRID_PATH)
    grid_utm = grid.to_crs(UTM_CRS)
    centroids_utm = grid_utm.geometry.centroid
    centroids_gdf = gpd.GeoDataFrame(
        {"grid_cell_id": grid["grid_cell_id"]}, geometry=centroids_utm, crs=UTM_CRS
    ).to_crs(WGS84_CRS)
    centroids_gdf["lat"] = centroids_gdf.geometry.y
    centroids_gdf["lon"] = centroids_gdf.geometry.x

    with rasterio.open(MOSAIC_PATH) as src:
        print(f"Mosaic size: {src.width}x{src.height}, resolution: {src.res}")
        elevation = src.read(1).astype(float)
        elevation[elevation < -1000] = np.nan  # SRTM no-data sentinel

        # Compute slope in degrees using the gradient method.
        # Pixel size in degrees converted to approximate meters (SRTM ~90m at equator).
        pixel_size_m = abs(src.res[0]) * 111320  # degrees to meters approximation
        dy, dx = np.gradient(elevation, pixel_size_m)
        slope_rad = np.arctan(np.sqrt(dx**2 + dy**2))
        slope_deg = np.degrees(slope_rad)

        results = []
        for _, row in centroids_gdf.iterrows():
            r, c = src.index(row["lon"], row["lat"])
            if 0 <= r < elevation.shape[0] and 0 <= c < elevation.shape[1]:
                elev_val = elevation[r, c]
                slope_val = slope_deg[r, c]
            else:
                elev_val, slope_val = None, None

            results.append({
                "grid_cell_id": row["grid_cell_id"],
                "elevation_m": round(float(elev_val), 1) if elev_val is not None and not np.isnan(elev_val) else None,
                "slope_deg": round(float(slope_val), 2) if slope_val is not None and not np.isnan(slope_val) else None,
            })

    import pandas as pd
    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nExtracted terrain features for {len(results_df)} grid cells.")
    print(f"Saved to {OUTPUT_PATH}")
    print("\nSample results:")
    print(results_df.head(10).to_string(index=False))

    summary = f"""Milestone 3.7 - SRTM Terrain Feature Extraction Summary
============================================================

Grid cells processed: {len(results_df)}
Source: CGIAR-CSI SRTM 90m v4.1, 4 tiles merged (43_12, 43_13, 44_12, 44_13)
Access method: direct HTTPS download, no authentication, with retry/backoff

Elevation: extracted at grid cell centroid.
Slope: computed via gradient method (numpy.gradient), degrees, using
SRTM's ~90m native resolution.

Elevation/slope statistics:
{results_df[['elevation_m', 'slope_deg']].describe().to_string()}
"""
    with open(SUMMARY_PATH, "w") as f:
        f.write(summary)
    print(f"\nSaved summary to {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
