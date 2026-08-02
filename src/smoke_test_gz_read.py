"""
Smoke test (fixed) - correct rasterio URI syntax for direct compressed
reads: gz+file:// scheme with proper file URI formatting (forward slashes,
triple-slash for absolute paths), required on Windows.
"""

from pathlib import Path
import rasterio

test_file = Path("data/external/chirps_cache/2024/chirps-v2.0.2024.01.15.tif.gz").resolve()
uri = f"gz+file:///{test_file.as_posix()}"
print(f"Testing URI: {uri}")

AHERO_LAT, AHERO_LON = -0.1496144, 34.9263121

with rasterio.open(uri) as src:
    print(f"Opened successfully. Raster size: {src.width}x{src.height}")
    row, col = src.index(AHERO_LON, AHERO_LAT)
    value = src.read(1)[row, col].item()
    print(f"Rainfall at Ahero on 2024-01-15: {value} mm")
    print("(Should match Milestone 2.3 pilot's 25.94mm)")
