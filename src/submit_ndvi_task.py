"""
Milestone 3.6 - Submit MODIS NDVI AppEEARS point task for all 20 unique
grid cells needed, requesting full available MODIS history (2000-present).

This gives us both:
1. The nearest composite at/before each record's observation date
2. Enough per-cell history to compute a genuine seasonal NDVI anomaly
   baseline (per Log Entry 006)

Output: reports/milestone_3_6_appeears_task_id.txt
"""

import getpass
import requests
import pandas as pd
import geopandas as gpd

APPEEARS_API = "https://appeears.earthdatacloud.nasa.gov/api"
GRID_PATH = "data/processed/analysis_grid.geojson"
OCCURRENCES_PATH = "data/processed/occurrences_with_grid_cell.csv"
UTM_CRS = "EPSG:32736"
WGS84_CRS = "EPSG:4326"


def login():
    username = input("Earthdata username: ")
    password = getpass.getpass("Earthdata password (hidden as you type): ")
    response = requests.post(f"{APPEEARS_API}/login", auth=(username, password), timeout=30)
    response.raise_for_status()
    return response.json()["token"]


def main():
    occ = pd.read_csv(OCCURRENCES_PATH)
    occ["year"] = pd.to_numeric(occ["year"], errors="coerce")
    candidates = occ[(occ["year"] >= 2000) & (occ["grid_cell_id"].notna())]
    unique_cell_ids = candidates["grid_cell_id"].unique().tolist()
    print(f"Unique grid cells: {len(unique_cell_ids)}")

    grid = gpd.read_file(GRID_PATH)
    grid_utm = grid.to_crs(UTM_CRS)
    centroids_utm = grid_utm.geometry.centroid
    centroids_gdf = gpd.GeoDataFrame(
        {"grid_cell_id": grid["grid_cell_id"]}, geometry=centroids_utm, crs=UTM_CRS
    ).to_crs(WGS84_CRS)
    centroids_gdf["lat"] = centroids_gdf.geometry.y
    centroids_gdf["lon"] = centroids_gdf.geometry.x
    centroids = centroids_gdf.set_index("grid_cell_id")

    coordinates = []
    for cell_id in unique_cell_ids:
        if cell_id in centroids.index:
            coordinates.append({
                "id": cell_id,
                "latitude": centroids.loc[cell_id, "lat"],
                "longitude": centroids.loc[cell_id, "lon"],
                "category": "QueleaGuard analysis grid cell",
            })

    print(f"Prepared {len(coordinates)} coordinates for AppEEARS request.")

    token = login()
    headers = {"Authorization": f"Bearer {token}"}

    task = {
        "task_type": "point",
        "task_name": "queleaguard_ndvi_full_history_20cells",
        "params": {
            "dates": [{"startDate": "01-01-2000", "endDate": "12-31-2026"}],
            "layers": [{"product": "MOD13Q1.061", "layer": "_250m_16_days_NDVI"}],
            "coordinates": coordinates,
        },
    }

    response = requests.post(f"{APPEEARS_API}/task", json=task, headers=headers, timeout=30)
    response.raise_for_status()
    task_id = response.json()["task_id"]
    print(f"\nTask submitted successfully. Task ID: {task_id}")

    with open("reports/milestone_3_6_appeears_task_id.txt", "w") as f:
        f.write(f"AppEEARS task ID: {task_id}\n")
        f.write(f"Submitted for: MOD13Q1.061 NDVI, {len(coordinates)} grid cells, 2000-2026 full history\n")
        f.write("Check status before downloading (may take longer than the single-point Milestone 2.6 pilot).\n")

    print("Task ID saved. AppEEARS processing for 20 points x ~26 years may take longer than")
    print("the single-point pilot did - check status before assuming it's ready.")


if __name__ == "__main__":
    main()
