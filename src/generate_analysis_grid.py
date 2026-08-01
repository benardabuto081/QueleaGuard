"""
Milestone 3.1 (continued) - Generate the 5.5km x 5.5km regular grid across
the analysis extent (Ahero Irrigation Scheme + 50km ecological buffer),
per the spatial framework adopted in Log Entry 002.

Process:
1. Load the confirmed Ahero boundary polygon.
2. Reproject to a metric coordinate system (UTM Zone 36S - correct local
   zone for western Kenya) so distances are in real meters, not degrees.
3. Buffer the boundary by 50,000 meters.
4. Tile a regular 5,500m x 5,500m grid across the buffered extent's
   bounding box.
5. Flag each cell as within_scheme_boundary (True/False) based on whether
   it intersects the original (unbuffered) Ahero polygon.
6. Reproject the grid back to standard lat/lon (EPSG:4326) for storage.

Output: data/processed/analysis_grid.geojson
        reports/milestone_3_1_grid_generation_summary.txt
"""

import geopandas as gpd
from shapely.geometry import box

BOUNDARY_PATH = "data/external/ahero_boundary.geojson"
OUTPUT_PATH = "data/processed/analysis_grid.geojson"
SUMMARY_PATH = "reports/milestone_3_1_grid_generation_summary.txt"

BUFFER_METERS = 50_000
CELL_SIZE_METERS = 5_500
UTM_CRS = "EPSG:32736"  # UTM Zone 36S - correct local metric CRS for western Kenya
WGS84_CRS = "EPSG:4326"  # standard lat/lon


def main():
    # 1. Load the confirmed Ahero boundary
    ahero = gpd.read_file(BOUNDARY_PATH)
    ahero_wgs84 = ahero.copy()

    # 2. Reproject to metric UTM for accurate buffering/gridding
    ahero_utm = ahero.to_crs(UTM_CRS)
    ahero_geom_utm = ahero_utm.geometry.iloc[0]

    # 3. Buffer by 50km in real meters
    analysis_extent_utm = ahero_geom_utm.buffer(BUFFER_METERS)
    minx, miny, maxx, maxy = analysis_extent_utm.bounds

    print(f"Ahero polygon area: {ahero_geom_utm.area / 1_000_000:.2f} sq km")
    print(f"Analysis extent (buffered) bounding box (meters, UTM 36S): "
          f"({minx:.0f}, {miny:.0f}) to ({maxx:.0f}, {maxy:.0f})")
    print(f"Analysis extent width: {(maxx - minx) / 1000:.1f} km, "
          f"height: {(maxy - miny) / 1000:.1f} km")

    # 4. Tile the regular grid across the bounding box
    cells = []
    x = minx
    while x < maxx:
        y = miny
        while y < maxy:
            cells.append(box(x, y, x + CELL_SIZE_METERS, y + CELL_SIZE_METERS))
            y += CELL_SIZE_METERS
        x += CELL_SIZE_METERS

    grid_utm = gpd.GeoDataFrame({"geometry": cells}, crs=UTM_CRS)
    print(f"\nTotal grid cells generated (bounding box): {len(grid_utm)}")

    # Keep only cells that actually intersect the buffered analysis extent
    # (not just its rectangular bounding box)
    grid_utm = grid_utm[grid_utm.intersects(analysis_extent_utm)].reset_index(drop=True)
    print(f"Grid cells intersecting the actual buffered extent: {len(grid_utm)}")

    # 5. Flag cells within the original (unbuffered) Ahero scheme boundary
    grid_utm["within_scheme_boundary"] = grid_utm.intersects(ahero_geom_utm)
    grid_utm["grid_cell_id"] = [f"cell_{i:04d}" for i in range(len(grid_utm))]

    within_count = grid_utm["within_scheme_boundary"].sum()
    print(f"Grid cells within the Ahero scheme boundary itself: {within_count}")
    print(f"Grid cells in the surrounding buffer only: {len(grid_utm) - within_count}")

    # 6. Reproject back to standard lat/lon for storage
    grid_wgs84 = grid_utm.to_crs(WGS84_CRS)
    grid_wgs84 = grid_wgs84[["grid_cell_id", "within_scheme_boundary", "geometry"]]
    grid_wgs84.to_file(OUTPUT_PATH, driver="GeoJSON")
    print(f"\nSaved grid to {OUTPUT_PATH}")

    summary = f"""Milestone 3.1 - Analysis Grid Generation Summary
====================================================

Source boundary: {BOUNDARY_PATH} (Ahero Irrigation Scheme, OpenStreetMap)
Ahero polygon area: {ahero_geom_utm.area / 1_000_000:.2f} sq km
Buffer applied: {BUFFER_METERS / 1000:.0f} km (Log Entry 002)
Grid cell size: {CELL_SIZE_METERS}m x {CELL_SIZE_METERS}m ({CELL_SIZE_METERS/1000}km, matching CHIRPS resolution)
Coordinate system used for buffering/gridding: {UTM_CRS} (UTM Zone 36S)

Analysis extent bounding box (meters): ({minx:.0f}, {miny:.0f}) to ({maxx:.0f}, {maxy:.0f})
Analysis extent dimensions: {(maxx - minx) / 1000:.1f} km x {(maxy - miny) / 1000:.1f} km

Total grid cells in final analysis grid: {len(grid_utm)}
Cells within Ahero scheme boundary: {within_count}
Cells in surrounding ecological buffer only: {len(grid_utm) - within_count}

Output file: {OUTPUT_PATH}
"""
    with open(SUMMARY_PATH, "w") as f:
        f.write(summary)
    print(f"Saved summary to {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
