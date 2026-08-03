"""
Milestone 3.7 (retry with resilience) - Download and mosaic SRTM tiles,
with retry/backoff for CGIAR's occasionally slow/unstable server.
"""

import math
import time
import requests
import zipfile
from pathlib import Path
import geopandas as gpd
import rasterio
from rasterio.merge import merge

GRID_PATH = "data/processed/analysis_grid.geojson"
CACHE_DIR = Path("data/external/srtm_cache")
MOSAIC_PATH = "data/external/srtm_mosaic.tif"
BASE_URL = "https://srtm.csi.cgiar.org/wp-content/uploads/files/srtm_5x5/TIFF"


def tile_col_row(lon, lat):
    col = math.floor((lon + 180) / 5) + 1
    row = math.floor((60 - lat) / 5) + 1
    return col, row


def download_with_retry(url, dest_path, retries=5, timeout=180):
    for attempt in range(1, retries + 1):
        try:
            print(f"  Attempt {attempt}/{retries}...")
            response = requests.get(url, timeout=timeout, stream=True)
            response.raise_for_status()
            with open(dest_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    f.write(chunk)
            return True
        except Exception as e:
            print(f"    Failed: {e}")
            if attempt < retries:
                wait = 10 * attempt
                print(f"    Retrying in {wait}s...")
                time.sleep(wait)
    return False


def main():
    grid = gpd.read_file(GRID_PATH)
    minx, miny, maxx, maxy = grid.total_bounds
    corners = [(minx, miny), (minx, maxy), (maxx, miny), (maxx, maxy)]
    tiles_needed = sorted(set(tile_col_row(lon, lat) for lon, lat in corners))
    print(f"SRTM tiles needed: {tiles_needed}")

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tile_paths = []

    for col, row in tiles_needed:
        tile_name = f"srtm_{col:02d}_{row:02d}"
        zip_path = CACHE_DIR / f"{tile_name}.zip"
        tif_path = CACHE_DIR / f"{tile_name}.tif"

        if not tif_path.exists():
            if not zip_path.exists() or zip_path.stat().st_size < 1_000_000:
                url = f"{BASE_URL}/{tile_name}.zip"
                print(f"Downloading {tile_name}...")
                success = download_with_retry(url, zip_path)
                if not success:
                    print(f"  FAILED after all retries: {tile_name}. Skipping for now.")
                    continue
                print(f"  Saved {zip_path} ({zip_path.stat().st_size/1e6:.1f} MB)")

            try:
                with zipfile.ZipFile(zip_path, "r") as zf:
                    zf.extractall(CACHE_DIR)
                print(f"  Extracted {tile_name}")
            except zipfile.BadZipFile:
                print(f"  WARNING: {zip_path} is not a valid zip (partial download?). Deleting for re-download.")
                zip_path.unlink()
                continue

        if tif_path.exists():
            tile_paths.append(tif_path)
        else:
            print(f"  WARNING: expected {tif_path} not found after extraction.")

    print(f"\nTiles ready: {len(tile_paths)} of {len(tiles_needed)} needed.")

    if len(tile_paths) < len(tiles_needed):
        print("Not all tiles downloaded successfully. Re-run this script to retry missing ones.")
        return

    if len(tile_paths) > 1:
        srcs = [rasterio.open(p) for p in tile_paths]
        mosaic, transform = merge(srcs)
        meta = srcs[0].meta.copy()
        meta.update({"height": mosaic.shape[1], "width": mosaic.shape[2], "transform": transform})
        with rasterio.open(MOSAIC_PATH, "w", **meta) as dst:
            dst.write(mosaic)
        for s in srcs:
            s.close()
        print(f"Merged {len(tile_paths)} tiles into {MOSAIC_PATH}")
    elif len(tile_paths) == 1:
        import shutil
        shutil.copy(tile_paths[0], MOSAIC_PATH)
        print(f"Single tile copied to {MOSAIC_PATH}")


if __name__ == "__main__":
    main()
