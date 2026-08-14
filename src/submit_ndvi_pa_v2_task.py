"""
Milestone 4.5 (Stage 1) - Submit AppEEARS task for the 45 grid cells
newly required by the corrected (month-stratified) pseudo-absence set,
not covered by any prior NDVI extraction (presence: 20 cells, v1
pseudo-absence gap-fill: 43 cells - see Log Entry 014 for why that v1
pool is now superseded).

Full history requested (2000-2026), same window as all prior NDVI tasks,
so seasonal baseline computation is consistent across the whole dataset.

Output: reports/milestone_4_5_ndvi_pa_v2_task_id.txt
"""

import getpass
import requests
import geopandas as gpd

APPEEARS_API = "https://appeears.earthdatacloud.nasa.gov/api"
GRID_PATH = "data/processed/analysis_grid.geojson"
UTM_CRS = "EPSG:32736"
WGS84_CRS = "EPSG:4326"

NEW_CELLS = ['cell_0000', 'cell_0011', 'cell_0020', 'cell_0033', 'cell_0039', 'cell_0046',
             'cell_0047', 'cell_0053', 'cell_0057', 'cell_0065', 'cell_0072', 'cell_0081',
             'cell_0101', 'cell_0106', 'cell_0107', 'cell_0119', 'cell_0124', 'cell_0126',
             'cell_0130', 'cell_0137', 'cell_0141', 'cell_0160', 'cell_0175', 'cell_0181',
             'cell_0182', 'cell_0184', 'cell_0194', 'cell_0199', 'cell_0201', 'cell_0203',
             'cell_0205', 'cell_0216', 'cell_0223', 'cell_0240', 'cell_0241', 'cell_0242',
             'cell_0243', 'cell_0251', 'cell_0253', 'cell_0260', 'cell_0265', 'cell_0278',
             'cell_0279', 'cell_0289', 'cell_0297']


def login():
    username = input("Earthdata username: ")
    password = getpass.getpass("Earthdata password (hidden as you type): ")
    response = requests.post(f"{APPEEARS_API}/login", auth=(username, password), timeout=30)
    response.raise_for_status()
    return response.json()["token"]


def main():
    print(f"Cells needing fresh NDVI (corrected PA set, v2): {len(NEW_CELLS)}")
    assert len(NEW_CELLS) == 45, f"Expected 45 cells, got {len(NEW_CELLS)} - list mismatch, do not proceed"

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
    missing_from_grid = []
    for cell_id in NEW_CELLS:
        if cell_id in centroids.index:
            lat = round(float(centroids.loc[cell_id, "lat"]), 6)
            lon = round(float(centroids.loc[cell_id, "lon"]), 6)
            coordinates.append({
                "id": cell_id, "latitude": lat, "longitude": lon,
                "category": "QueleaGuard pseudo-absence v2 grid cell",
            })
        else:
            missing_from_grid.append(cell_id)

    if missing_from_grid:
        print(f"WARNING: {len(missing_from_grid)} cell(s) not found in analysis grid: {missing_from_grid}")
        print("STOPPING - do not submit an incomplete/incorrect task.")
        return

    print(f"Prepared {len(coordinates)} coordinates. Sample: {coordinates[0]}")

    token = login()
    headers = {"Authorization": f"Bearer {token}"}

    task = {
        "task_type": "point",
        "task_name": "queleaguard_ndvi_pa_v2_gap_45cells",
        "params": {
            "dates": [{"startDate": "01-01-2000", "endDate": "12-31-2026"}],
            "layers": [{"product": "MOD13Q1.061", "layer": "_250m_16_days_NDVI"}],
            "coordinates": coordinates,
        },
    }

    response = requests.post(f"{APPEEARS_API}/task", json=task, headers=headers, timeout=30)
    if response.status_code != 200:
        print(f"Status: {response.status_code}")
        print(f"Body: {response.text}")
        return
    response.raise_for_status()
    task_id = response.json()["task_id"]
    print(f"\nTask submitted successfully. Task ID: {task_id}")

    with open("reports/milestone_4_5_ndvi_pa_v2_task_id.txt", "w") as f:
        f.write(f"AppEEARS task ID: {task_id}\n")
        f.write(f"Task name: queleaguard_ndvi_pa_v2_gap_45cells\n")
        f.write(f"Covers {len(coordinates)} grid cells newly required by corrected (v2) pseudo-absence set\n")
        f.write(f"Cell list: {NEW_CELLS}\n")
        f.write(f"Date range requested: 2000-01-01 to 2026-12-31\n")

    print("Task ID and cell list logged to reports/milestone_4_5_ndvi_pa_v2_task_id.txt")


if __name__ == "__main__":
    main()
