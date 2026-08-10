"""
Milestone 3.9 (NDVI gap fix, corrected) - Submit AppEEARS task for the 43
missing grid cells, with coordinates rounded and cast to plain Python
floats (fixes AppEEARS' rejection of numpy.float64's excessive decimal
precision).
"""

import getpass
import requests
import geopandas as gpd

APPEEARS_API = "https://appeears.earthdatacloud.nasa.gov/api"
GRID_PATH = "data/processed/analysis_grid.geojson"
UTM_CRS = "EPSG:32736"
WGS84_CRS = "EPSG:4326"

MISSING_CELLS = ['cell_0098', 'cell_0165', 'cell_0283', 'cell_0110', 'cell_0185', 'cell_0100',
                 'cell_0117', 'cell_0109', 'cell_0193', 'cell_0091', 'cell_0200', 'cell_0143',
                 'cell_0064', 'cell_0083', 'cell_0164', 'cell_0016', 'cell_0123', 'cell_0145',
                 'cell_0221', 'cell_0138', 'cell_0158', 'cell_0125', 'cell_0006', 'cell_0032',
                 'cell_0286', 'cell_0088', 'cell_0287', 'cell_0301', 'cell_0025', 'cell_0056',
                 'cell_0120', 'cell_0183', 'cell_0146', 'cell_0288', 'cell_0303', 'cell_0310',
                 'cell_0142', 'cell_0163', 'cell_0013', 'cell_0225', 'cell_0295', 'cell_0144',
                 'cell_0018']


def login():
    username = input("Earthdata username: ")
    password = getpass.getpass("Earthdata password (hidden as you type): ")
    response = requests.post(f"{APPEEARS_API}/login", auth=(username, password), timeout=30)
    response.raise_for_status()
    return response.json()["token"]


def main():
    print(f"Cells needing NDVI: {len(MISSING_CELLS)}")

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
    for cell_id in MISSING_CELLS:
        if cell_id in centroids.index:
            # Round to 6 decimal places (~0.11m precision - far finer than
            # our 5.5km grid needs) and cast to plain Python float.
            lat = round(float(centroids.loc[cell_id, "lat"]), 6)
            lon = round(float(centroids.loc[cell_id, "lon"]), 6)
            coordinates.append({
                "id": cell_id,
                "latitude": lat,
                "longitude": lon,
                "category": "QueleaGuard pseudo-absence grid cell",
            })

    print(f"Prepared {len(coordinates)} coordinates.")
    print(f"Sample coordinate: {coordinates[0]}")

    token = login()
    headers = {"Authorization": f"Bearer {token}"}

    task = {
        "task_type": "point",
        "task_name": "queleaguard_ndvi_pseudo_absence_gap_43cells",
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

    with open("reports/milestone_3_9_ndvi_gap_task_id.txt", "w") as f:
        f.write(f"AppEEARS task ID: {task_id}\n")
        f.write(f"Covers {len(coordinates)} grid cells missing NDVI (pseudo-absence gap fix)\n")


if __name__ == "__main__":
    main()
