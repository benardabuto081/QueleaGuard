"""
Milestone 4.5 (Stage 2) - Download completed AppEEARS NDVI bundle.

Task:
    queleaguard_ndvi_pa_v2_gap_45cells

Task ID:
    be74e08a-bee5-4418-acd1-e024b3582f93

Purpose:
    Download and preserve ALL AppEEARS output artifacts before any
    transformation or extraction.

No NDVI values are modified in this stage.
"""

import getpass
import os
import requests

APPEEARS_API = "https://appeears.earthdatacloud.nasa.gov/api"
TASK_ID = "be74e08a-bee5-4418-acd1-e024b3582f93"

OUTPUT_DIR = "data/external/appeears_ndvi_pa_v2_gap_45cells"


def login():
    username = input("Earthdata username: ")
    password = getpass.getpass("Earthdata password (hidden as you type): ")

    response = requests.post(
        f"{APPEEARS_API}/login",
        auth=(username, password),
        timeout=30,
    )

    response.raise_for_status()
    return response.json()["token"]


def main():
    print("=" * 70)
    print("QueleaGuard Milestone 4.5 - Download AppEEARS Bundle")
    print("=" * 70)
    print(f"Task ID: {TASK_ID}")
    print()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    token = login()
    headers = {"Authorization": f"Bearer {token}"}

    # Retrieve bundle manifest
    response = requests.get(
        f"{APPEEARS_API}/bundle/{TASK_ID}",
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()

    files = response.json()["files"]

    print(f"\nFound {len(files)} files in AppEEARS bundle.")

    downloaded = 0

    for item in files:
        file_name = item["file_name"]
        file_id = item["file_id"]

        output_path = os.path.join(OUTPUT_DIR, file_name)

        print("\n" + "-" * 70)
        print(f"Downloading: {file_name}")
        print(f"Expected size: {item.get('file_size')} bytes")
        print(f"Output: {output_path}")

        download_response = requests.get(
            f"{APPEEARS_API}/bundle/{TASK_ID}/{file_id}",
            headers=headers,
            timeout=120,
        )
        download_response.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(download_response.content)

        actual_size = os.path.getsize(output_path)

        print(f"Downloaded size: {actual_size} bytes")

        if item.get("file_size") is not None:
            if actual_size != int(item["file_size"]):
                raise RuntimeError(
                    f"SIZE MISMATCH for {file_name}: "
                    f"expected {item['file_size']}, got {actual_size}"
                )

        print("Verified: size matches AppEEARS manifest.")
        downloaded += 1

    # Write a local provenance record
    manifest_path = os.path.join(
        OUTPUT_DIR,
        "appeears_bundle_provenance.txt"
    )

    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write("QueleaGuard Milestone 4.5 - AppEEARS NDVI Provenance\n")
        f.write("=" * 60 + "\n")
        f.write(f"Task ID: {TASK_ID}\n")
        f.write("Task name: queleaguard_ndvi_pa_v2_gap_45cells\n")
        f.write("Product: MOD13Q1.061\n")
        f.write("Layer: _250m_16_days_NDVI\n")
        f.write("Purpose: Corrected v2 pseudo-absence NDVI gap, 45 cells\n")
        f.write("\nFiles downloaded from AppEEARS:\n")

        for item in files:
            f.write(
                f"- {item['file_name']} | "
                f"file_id={item['file_id']} | "
                f"size={item.get('file_size')}\n"
            )

    print("\n" + "=" * 70)
    print(f"Successfully downloaded {downloaded}/{len(files)} AppEEARS files.")
    print(f"Raw bundle preserved in: {OUTPUT_DIR}")
    print(f"Provenance record: {manifest_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
