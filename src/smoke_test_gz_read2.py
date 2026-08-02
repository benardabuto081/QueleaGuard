"""
Smoke test (attempt 2) - raw GDAL /vsigzip/ virtual filesystem prefix,
bypassing rasterio's URI scheme translation.
"""

from pathlib import Path
import rasterio

test_file = Path("data/external/chirps_cache/2024/chirps-v2.0.2024.01.15.tif.gz").resolve()
vsi_path = f"/vsigzip/{test_file.as_posix()}"
print(f"Testing path: {vsi_path}")

AHERO_LAT, AHERO_LON = -0.1496144, 34.9263121

with rasterio.open(vsi_path) as src:
    print(f"Opened successfully. Raster size: {src.width}x{src.height}")
    row, col = src.index(AHERO_LON, AHERO_LAT)
    value = src.read(1)[row, col].item()
    print(f"Rainfall at Ahero on 2024-01-15: {value} mm")
