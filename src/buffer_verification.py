"""
Milestone 2.4 (continued) - Verify occurrence record coverage within a
true 50km radius of Ahero, to support the analysis-extent buffer decision
with actual data rather than an approximation from the Milestone 2.1
rectangular bounding boxes.

Output: reports/milestone_2_4_buffer_verification.txt
"""

import math
import pandas as pd

AHERO_LAT = -0.1496144
AHERO_LON = 34.9263121
EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1, lon1, lat2, lon2):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def main():
    df = pd.read_csv("data/raw/gbif_kisumu_county_raw.csv")

    df["distance_km_from_ahero"] = df.apply(
        lambda row: haversine_km(AHERO_LAT, AHERO_LON, row["decimalLatitude"], row["decimalLongitude"]),
        axis=1,
    )

    lines = []
    lines.append("Milestone 2.4 - Buffer Distance Verification (50km radius)")
    lines.append("=" * 60)
    lines.append(f"Total records (Milestone 2.1 Kisumu County pull): {len(df)}")
    lines.append("")

    for radius in [15, 30, 50, 75, 100]:
        count = (df["distance_km_from_ahero"] <= radius).sum()
        pct = 100 * count / len(df)
        lines.append(f"Records within {radius} km of Ahero: {count} ({pct:.1f}%)")

    lines.append("")
    lines.append(f"Nearest record: {df['distance_km_from_ahero'].min():.1f} km")
    lines.append(f"Farthest record: {df['distance_km_from_ahero'].max():.1f} km")
    lines.append(f"Median distance: {df['distance_km_from_ahero'].median():.1f} km")

    output = "\n".join(lines)
    print(output)

    with open("reports/milestone_2_4_buffer_verification.txt", "w") as f:
        f.write(output)
    print("\n\nSaved to reports/milestone_2_4_buffer_verification.txt")


if __name__ == "__main__":
    main()
