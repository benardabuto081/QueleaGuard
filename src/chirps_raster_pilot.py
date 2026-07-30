"""
Milestone 2.3 - CHIRPS raster access pilot.

Downloads one day of global CHIRPS daily rainfall (GeoTIFF) directly from
the CHIRPS public data server, then extracts the rainfall value at the
Ahero Irrigation Scheme coordinate using rasterio.

Confirms the raw-raster access path (no authentication required) and
records the result as a reference output for future documentation/publication
use, per the project's publication-readiness engineering goal.

Outputs:
  data/external/chirps_20240115_global.tif
  reports/milestone_2_3_chirps_pilot_result.txt
"""

import gzip
import requests
import rasterio

AHERO_LAT = -0.1496144
AHERO_LON = 34.9263121

CHIRPS_URL = "https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05/2024/chirps-v2.0.2024.01.15.tif.gz"


def main():
    gz_path = "data/external/chirps_20240115_global.tif.gz"
    tif_path = "data/external/chirps_20240115_global.tif"

    print(f"Downloading CHIRPS daily file: {CHIRPS_URL}")
    response = requests.get(CHIRPS_URL, timeout=120)
    response.raise_for_status()

    with open(gz_path, "wb") as f:
        f.write(response.content)
    file_size_mb = len(response.content) / 1_000_000
    print(f"Saved compressed file: {gz_path} ({file_size_mb:.1f} MB)")

    with gzip.open(gz_path, "rb") as f_in, open(tif_path, "wb") as f_out:
        f_out.write(f_in.read())
    print(f"Decompressed to: {tif_path}")

    with rasterio.open(tif_path) as src:
        width, height = src.width, src.height
        resolution = src.res
        row, col = src.index(AHERO_LON, AHERO_LAT)
        # .item() converts the single NumPy value to a plain Python float,
        # avoiding the deprecated array-indexing-returns-0d-array pattern.
        value = src.read(1)[row, col].item()

    print(f"\nRaster info: {width}x{height} pixels, resolution: {resolution}")
    print(f"Rainfall at Ahero (-0.1496, 34.9263) on 2024-01-15: {value:.2f} mm")

    # Save a small, human-readable reference result for documentation/publication use.
    result_summary = f"""Milestone 2.3 - CHIRPS Rainfall Data Access Pilot
=================================================

Date of test: 2024-01-15
Location: Ahero Irrigation Scheme ({AHERO_LAT}, {AHERO_LON})
Source: CHIRPS v2.0 daily, p05 (0.05 degree, ~5.5km resolution)
Access method: Direct HTTPS download from data.chc.ucsb.edu (public, no authentication)
File size (compressed): {file_size_mb:.1f} MB
Raster dimensions: {width} x {height} pixels
Confirmed resolution: {resolution[0]:.4f} degrees (~5.5 km)

Result: {value:.2f} mm rainfall recorded at Ahero on 2024-01-15

Conclusion: CHIRPS raster access confirmed feasible via public HTTPS,
no authentication required. Value extraction via rasterio successful.
Approved as primary rainfall source per Dataset Feasibility Study, Section 7.
"""
    with open("reports/milestone_2_3_chirps_pilot_result.txt", "w") as f:
        f.write(result_summary)
    print("\nSaved reference result to reports/milestone_2_3_chirps_pilot_result.txt")


if __name__ == "__main__":
    main()
