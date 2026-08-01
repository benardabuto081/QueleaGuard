"""
Milestone 3.2 (continued) - Determine cell_0080's location relative to
Ahero and known water features, using the coordinates already confirmed.
"""

import math

AHERO_LAT, AHERO_LON = -0.1496144, 34.9263121
CELL_LAT, CELL_LON = -0.125407, 34.742504  # cell_0080 representative point

EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1, lon1, lat2, lon2):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


distance = haversine_km(AHERO_LAT, AHERO_LON, CELL_LAT, CELL_LON)
bearing_lon_diff = CELL_LON - AHERO_LON
direction = "west" if bearing_lon_diff < 0 else "east"

print(f"cell_0080 representative point: ({CELL_LAT}, {CELL_LON})")
print(f"Distance from Ahero: {distance:.1f} km")
print(f"Direction from Ahero: approximately due {direction} (longitude difference: {bearing_lon_diff:.4f} degrees)")
print(f"\nFor reference: Lake Victoria's Winam Gulf shoreline near Kisumu sits at approximately -0.10, 34.75")
print("This site's coordinates are close to that reference point.")
