"""
Milestone 2.3 - CHIRPS rainfall data access pilot.

Pulls one month of daily rainfall for the Ahero Irrigation Scheme coordinate
via the IRI Climate Data Library's point-extraction service, which serves
CHIRPS as CSV directly rather than requiring raw raster downloads.

This confirms access method, format, and real values before committing to
a full historical pull.

Output: data/external/chirps_ahero_pilot_jan2024.csv
"""

import requests

AHERO_LAT = -0.1496144
AHERO_LON = 34.9263121

IRI_URL = (
    "https://iridl.ldeo.columbia.edu/SOURCES/.UCSB/.CHIRPS/.v2p0/"
    ".daily-improved/.global/.0p05/.prcp/"
    f"X/{AHERO_LON}/VALUE/"
    f"Y/{AHERO_LAT}/VALUE/"
    "T/(1 Jan 2024)/(31 Jan 2024)/RANGEEDGES/"
    "data.csv"
)


def main():
    print("Requesting CHIRPS rainfall data for Ahero (Jan 2024) via IRI Data Library...")
    response = requests.get(IRI_URL, timeout=60)
    response.raise_for_status()

    output_path = "data/external/chirps_ahero_pilot_jan2024.csv"
    with open(output_path, "wb") as f:
        f.write(response.content)

    print(f"Saved response to {output_path}")
    print("\nFirst 15 lines of the response:")
    lines = response.text.splitlines()
    for line in lines[:15]:
        print(line)


if __name__ == "__main__":
    main()
