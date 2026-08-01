"""
Milestone 2.5 - NASA POWER meteorology access pilot.

Pulls one month of daily temperature, humidity, and wind speed for Ahero's
coordinates via NASA POWER's public REST API (no authentication required),
to confirm access and real values before the NASA POWER vs. ERA5-Land
decision.

Output: reports/milestone_2_5_nasa_power_pilot_result.txt
"""

import requests

AHERO_LAT = -0.1496144
AHERO_LON = 34.9263121

POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

PARAMS = {
    "parameters": "T2M,RH2M,WS2M",  # temp at 2m, relative humidity at 2m, wind speed at 2m
    "community": "AG",
    "longitude": AHERO_LON,
    "latitude": AHERO_LAT,
    "start": "20240101",
    "end": "20240131",
    "format": "JSON",
}


def main():
    print("Requesting NASA POWER data for Ahero (Jan 2024)...")
    response = requests.get(POWER_URL, params=PARAMS, timeout=60)
    response.raise_for_status()
    data = response.json()

    params_data = data["properties"]["parameter"]
    dates = sorted(params_data["T2M"].keys())

    lines = []
    lines.append("Milestone 2.5 - NASA POWER Access Pilot")
    lines.append("=" * 60)
    lines.append(f"Location: Ahero ({AHERO_LAT}, {AHERO_LON})")
    lines.append(f"Period: {dates[0]} to {dates[-1]}")
    lines.append(f"Resolution (per NASA POWER documentation): ~0.5 x 0.625 degrees (~50-55 km)")
    lines.append("")
    lines.append("Sample daily values (first 5 days):")
    for d in dates[:5]:
        t2m = params_data["T2M"][d]
        rh2m = params_data["RH2M"][d]
        ws2m = params_data["WS2M"][d]
        lines.append(f"  {d}: Temp={t2m}C, RH={rh2m}%, Wind={ws2m}m/s")

    lines.append("")
    lines.append(f"Total days retrieved: {len(dates)}")
    lines.append("Access method: Direct HTTPS GET, no authentication required")

    output = "\n".join(lines)
    print("\n" + output)

    with open("reports/milestone_2_5_nasa_power_pilot_result.txt", "w") as f:
        f.write(output)
    print("\n\nSaved to reports/milestone_2_5_nasa_power_pilot_result.txt")


if __name__ == "__main__":
    main()
