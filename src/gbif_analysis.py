"""
Milestone 2.1 (continued) - Data quality and distribution analysis of the
downloaded GBIF Kisumu County occurrence records.

Evaluates: spatial distribution, temporal coverage, coordinate uncertainty,
basis of record, duplicate records, and overall data quality - per the
evaluation criteria set before any study-area decision is made.
"""

import pandas as pd

INPUT_PATH = "data/raw/gbif_kisumu_county_raw.csv"


def main():
    df = pd.read_csv(INPUT_PATH)
    print(f"Total records: {len(df)}\n")

    # --- Spatial distribution ---
    print("=" * 60)
    print("SPATIAL DISTRIBUTION")
    print("=" * 60)
    print(df[["decimalLatitude", "decimalLongitude"]].describe())
    print()
    # Ahero/Nyamware sit roughly at -0.15 lat, 34.9 lon.
    # Count how many records fall within the original ~15km "tight" box.
    tight_mask = (
        df["decimalLatitude"].between(-0.35, 0.05)
        & df["decimalLongitude"].between(34.75, 35.05)
    )
    print(f"Records falling within the original tight scheme-area box: {tight_mask.sum()} of {len(df)}")
    print(f"Records outside that box but within county: {(~tight_mask).sum()}")
    print()

    # --- Temporal coverage ---
    print("=" * 60)
    print("TEMPORAL COVERAGE")
    print("=" * 60)
    print(f"Year range: {df['year'].min()} - {df['year'].max()}")
    print("\nRecords per year:")
    print(df["year"].value_counts().sort_index())
    print("\nRecords per month (all years combined):")
    print(df["month"].value_counts().sort_index())
    print()

    # --- Coordinate uncertainty ---
    print("=" * 60)
    print("COORDINATE UNCERTAINTY")
    print("=" * 60)
    non_null_uncertainty = df["coordinateUncertaintyInMeters"].notna().sum()
    print(f"Records WITH reported coordinate uncertainty: {non_null_uncertainty}")
    print(f"Records WITHOUT reported coordinate uncertainty: {len(df) - non_null_uncertainty}")
    if non_null_uncertainty > 0:
        print("\nDistribution of reported uncertainty (meters), where available:")
        print(df["coordinateUncertaintyInMeters"].describe())
    print()

    # --- Basis of record ---
    print("=" * 60)
    print("BASIS OF RECORD")
    print("=" * 60)
    print(df["basisOfRecord"].value_counts())
    print()

    # --- Data source (dataset) breakdown ---
    print("=" * 60)
    print("SOURCE DATASET BREAKDOWN")
    print("=" * 60)
    print(df["datasetKey"].value_counts())
    print()

    # --- Duplicate check ---
    print("=" * 60)
    print("DUPLICATE RECORDS")
    print("=" * 60)
    exact_coord_time_dupes = df.duplicated(
        subset=["decimalLatitude", "decimalLongitude", "eventDate"], keep=False
    ).sum()
    print(f"Records sharing identical lat/lon/date with at least one other record: {exact_coord_time_dupes}")
    id_dupes = df.duplicated(subset=["occurrenceID"], keep=False).sum()
    print(f"Records with duplicate occurrenceID: {id_dupes}")
    print()

    # --- Missing data summary ---
    print("=" * 60)
    print("MISSING DATA SUMMARY")
    print("=" * 60)
    print(df.isna().sum())


if __name__ == "__main__":
    main()
