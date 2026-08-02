"""
Diagnostic - inspect the actual file type/format of a downloaded
ERA5-Land file, since xarray failed to recognize it as NetCDF.
"""

from pathlib import Path

sample = Path("data/external/era5land_cache/era5land_2000_10.nc")
print(f"File exists: {sample.exists()}")
print(f"File size: {sample.stat().st_size} bytes")

with open(sample, "rb") as f:
    header = f.read(16)
print(f"First 16 bytes (hex): {header.hex()}")
print(f"First 16 bytes (raw): {header}")

# Common signatures:
# NetCDF classic: b'CDF\x01' or b'CDF\x02'
# NetCDF4/HDF5:   b'\x89HDF\r\n\x1a\n'
# ZIP archive:    b'PK\x03\x04'
