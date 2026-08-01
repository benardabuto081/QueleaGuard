"""
Milestone 2.5 (continued) - ERA5-Land meteorology access pilot.

Requests one day of ERA5-Land hourly temperature, humidity-related
(dewpoint), and wind data for Ahero's coordinates via the Copernicus
Climate Data Store API, to compare against the NASA POWER pilot.

Note: CDS requests are queued and processed server-side, so this may
take anywhere from under a minute to several minutes depending on
current queue load - this is normal, not an error.

Output: data/external/era5land_ahero_20240115.nc
        reports/milestone_2_5_era5land_pilot_result.txt
"""

import cdsapi

AHERO_LAT = -0.1496144
AHERO_LON = 34.9263121

# Small bounding box around Ahero: [North, West, South, East]
AREA = [AHERO_LAT + 0.1, AHERO_LON - 0.1, AHERO_LAT - 0.1, AHERO_LON + 0.1]


def main():
    client = cdsapi.Client()

    dataset = "reanalysis-era5-land"
    request = {
        "variable": ["2m_temperature", "2m_dewpoint_temperature", "10m_u_component_of_wind", "10m_v_component_of_wind"],
        "year": "2024",
        "month": "01",
        "day": "15",
        "time": ["00:00", "06:00", "12:00", "18:00"],
        "area": AREA,
        "data_format": "netcdf",
    }
    target = "data/external/era5land_ahero_20240115.nc"

    print("Submitting ERA5-Land request to Copernicus CDS...")
    print("This may take a few minutes - the request is queued server-side.")
    client.retrieve(dataset, request, target)
    print(f"\nDownload complete: {target}")

    result_summary = f"""Milestone 2.5 - ERA5-Land Access Pilot
=========================================

Date of test: 2024-01-15
Location: Ahero area (bounding box: {AREA})
Source: ERA5-Land reanalysis, Copernicus Climate Data Store
Access method: cdsapi Python client, authenticated via personal API key
Resolution (per ERA5-Land documentation): ~9 km

Result: Successfully downloaded NetCDF file: {target}

Conclusion: ERA5-Land access confirmed feasible via CDS API, requires
free registration and API key (unlike NASA POWER's no-auth access).
Resolution (~9km) is substantially finer than NASA POWER (~50-55km) and
closer to (though still coarser than) our adopted 5.5km grid.
"""
    with open("reports/milestone_2_5_era5land_pilot_result.txt", "w") as f:
        f.write(result_summary)
    print("\nSaved reference result to reports/milestone_2_5_era5land_pilot_result.txt")


if __name__ == "__main__":
    main()
