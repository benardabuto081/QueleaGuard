import pandas as pd
from pathlib import Path

print("=" * 100)
print("QUELEAGUARD — PSEUDO-ABSENCE RECORD-LEVEL LINEAGE AUDIT")
print("=" * 100)

BASE = Path("data/processed")

files = {
    "pa_final": BASE / "pseudo_absences_final.csv",
    "rainfall": BASE / "rainfall_features_pseudo_absence.csv",
    "meteorology": BASE / "meteorology_features_pseudo_absence.csv",
    "ndvi": BASE / "ndvi_features_pseudo_absence.csv",
    "modelling": BASE / "modelling_dataset_final.csv",
}

dfs = {}

for name, path in files.items():
    print(f"\nLoading {name}: {path}")

    if not path.exists():
        print(f"  ERROR: file missing")
        continue

    df = pd.read_csv(path)
    dfs[name] = df

    print(f"  Rows: {len(df)}")
    print(f"  Columns: {list(df.columns)}")


# ---------------------------------------------------------------------------
# 1. NORMALISE IDENTIFIERS
# ---------------------------------------------------------------------------

print("\n" + "=" * 100)
print("1. NORMALISING RECORD IDENTIFIERS")
print("=" * 100)

pa = dfs["pa_final"].copy()
rain = dfs["rainfall"].copy()
met = dfs["meteorology"].copy()
ndvi = dfs["ndvi"].copy()
model = dfs["modelling"].copy()

# Record key is the authoritative identity where available.
for df_name, df in [
    ("pa_final", pa),
    ("rainfall", rain),
    ("meteorology", met),
]:
    if "key" in df.columns:
        df["record_key"] = df["key"].astype(str).str.strip()

    if "record_key" in df.columns:
        df["record_key"] = df["record_key"].astype(str).str.strip()

# NDVI does not appear to carry record_key.
# Build a date + grid identity for NDVI diagnostics.
for df in [pa, rain, met, ndvi, model]:
    if "grid_cell_id" in df.columns:
        df["grid_cell_id"] = df["grid_cell_id"].astype(str).str.strip()

    for col in ["eventDate", "event_date", "observation_date", "ndvi_aligned_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(
                df[col],
                errors="coerce"
            ).dt.normalize()

# Modelling dataset
model["record_key"] = model["record_key"].astype(str).str.strip()


# ---------------------------------------------------------------------------
# 2. CHECK DUPLICATE RECORD KEYS
# ---------------------------------------------------------------------------

print("\n" + "=" * 100)
print("2. DUPLICATE RECORD-KEY CHECK")
print("=" * 100)

for name, df in [
    ("pseudo_absences_final", pa),
    ("rainfall", rain),
    ("meteorology", met),
    ("modelling_dataset_final", model),
]:

    if "record_key" not in df.columns:
        continue

    dup = df[df["record_key"].duplicated(keep=False)]

    print(f"\n{name}:")
    print(f"  Rows: {len(df)}")
    print(f"  Unique record keys: {df['record_key'].nunique()}")
    print(f"  Duplicate rows: {len(dup)}")

    if len(dup):
        print(dup[["record_key"]].drop_duplicates().head(20).to_string(index=False))


# ---------------------------------------------------------------------------
# 3. AUTHORITATIVE PSEUDO-ABSENCE SET
# ---------------------------------------------------------------------------

print("\n" + "=" * 100)
print("3. AUTHORITATIVE PSEUDO-ABSENCE SET")
print("=" * 100)

pa_keys = set(pa["record_key"])

print(f"Pseudo-absence records: {len(pa)}")
print(f"Unique pseudo-absence keys: {len(pa_keys)}")


# ---------------------------------------------------------------------------
# 4. RECORD PRESENCE THROUGH EACH ENVIRONMENTAL STAGE
# ---------------------------------------------------------------------------

print("\n" + "=" * 100)
print("4. RECORD-BY-RECORD PIPELINE SURVIVAL")
print("=" * 100)

rain_keys = set(rain["record_key"])
met_keys = set(met["record_key"])
model_keys = set(model.loc[model["presence"] == 0, "record_key"])

# NDVI is cell/date based rather than record-key based.
# We therefore construct candidate NDVI matches below.

rows = []

for _, r in pa.iterrows():

    key = str(r["record_key"])
    cell = str(r["grid_cell_id"])

    event_date = pd.to_datetime(
        r["eventDate"],
        errors="coerce"
    )

    event_date = (
        event_date.normalize()
        if not pd.isna(event_date)
        else pd.NaT
    )

    rainfall_present = key in rain_keys
    meteorology_present = key in met_keys
    modelling_present = key in model_keys

    # Exact event-date NDVI match
    ndvi_exact = ndvi[
        (ndvi["grid_cell_id"] == cell) &
        (ndvi["event_date"] == event_date)
    ]

    # If exact date isn't available, look for any NDVI record
    # in the same cell.
    ndvi_cell = ndvi[
        ndvi["grid_cell_id"] == cell
    ]

    rows.append({
        "record_key": key,
        "grid_cell_id": cell,
        "event_date": event_date.date()
            if not pd.isna(event_date)
            else None,
        "rainfall_present": rainfall_present,
        "meteorology_present": meteorology_present,
        "ndvi_exact_date_match": len(ndvi_exact) > 0,
        "ndvi_same_cell_match": len(ndvi_cell) > 0,
        "ndvi_matches_same_cell": len(ndvi_cell),
        "in_final_model": modelling_present,
    })

lineage = pd.DataFrame(rows)

print("\nPipeline survival:")
print(
    f"  Starting pseudo-absences : {len(lineage)}"
)
print(
    f"  Rainfall available       : {lineage['rainfall_present'].sum()}"
)
print(
    f"  Meteorology available    : {lineage['meteorology_present'].sum()}"
)
print(
    f"  NDVI exact date match    : {lineage['ndvi_exact_date_match'].sum()}"
)
print(
    f"  NDVI same-cell available : {lineage['ndvi_same_cell_match'].sum()}"
)
print(
    f"  Final modelling dataset  : {lineage['in_final_model'].sum()}"
)


# ---------------------------------------------------------------------------
# 5. THE SEVEN MISSING RECORDS
# ---------------------------------------------------------------------------

print("\n" + "=" * 100)
print("5. PSEUDO-ABSENCE RECORDS MISSING FROM FINAL MODEL")
print("=" * 100)

missing_final = lineage[
    ~lineage["in_final_model"]
].copy()

print(f"\nMissing from final modelling dataset: {len(missing_final)}")

if len(missing_final):

    print(
        missing_final.to_string(index=False)
    )

    print("\nDetailed source records:")

    details = pa[
        pa["record_key"].isin(
            missing_final["record_key"]
        )
    ].copy()

    cols = [
        c for c in [
            "record_key",
            "key",
            "scientificName",
            "decimalLatitude",
            "decimalLongitude",
            "eventDate",
            "year",
            "grid_cell_id",
            "within_scheme_boundary",
        ]
        if c in details.columns
    ]

    print(
        details[cols].to_string(index=False)
    )


# ---------------------------------------------------------------------------
# 6. CHECK WHETHER THE MISSING RECORDS ARE MISSING RAINFALL
# ---------------------------------------------------------------------------

print("\n" + "=" * 100)
print("6. RAINFALL FAILURE ANALYSIS")
print("=" * 100)

rainfall_missing = lineage[
    ~lineage["rainfall_present"]
]

print(
    f"Pseudo-absence records without rainfall: "
    f"{len(rainfall_missing)}"
)

if len(rainfall_missing):
    print(
        rainfall_missing.to_string(index=False)
    )


# ---------------------------------------------------------------------------
# 7. CHECK WHETHER THE MISSING RECORDS ARE MISSING METEOROLOGY
# ---------------------------------------------------------------------------

print("\n" + "=" * 100)
print("7. METEOROLOGY FAILURE ANALYSIS")
print("=" * 100)

met_missing = lineage[
    ~lineage["meteorology_present"]
]

print(
    f"Pseudo-absence records without meteorology: "
    f"{len(met_missing)}"
)

if len(met_missing):
    print(
        met_missing.to_string(index=False)
    )


# ---------------------------------------------------------------------------
# 8. CHECK NDVI AVAILABILITY FOR THE MISSING RECORDS
# ---------------------------------------------------------------------------

print("\n" + "=" * 100)
print("8. NDVI FAILURE ANALYSIS")
print("=" * 100)

ndvi_problem = lineage[
    ~lineage["ndvi_same_cell_match"]
]

print(
    f"Pseudo-absence records whose grid cell has NO NDVI record: "
    f"{len(ndvi_problem)}"
)

if len(ndvi_problem):
    print(
        ndvi_problem.to_string(index=False)
    )

print("\nMissing-final records and their NDVI status:")

print(
    missing_final[
        [
            "record_key",
            "grid_cell_id",
            "event_date",
            "ndvi_exact_date_match",
            "ndvi_same_cell_match",
            "ndvi_matches_same_cell",
        ]
    ].to_string(index=False)
)


# ---------------------------------------------------------------------------
# 9. FINAL MODEL PSEUDO-ABSENCE KEYS
# ---------------------------------------------------------------------------

print("\n" + "=" * 100)
print("9. FINAL DATASET PSEUDO-ABSENCE CHECK")
print("=" * 100)

model_pa = model[
    model["presence"] == 0
].copy()

print(
    f"Pseudo-absence rows in final dataset: {len(model_pa)}"
)
print(
    f"Unique pseudo-absence record keys: "
    f"{model_pa['record_key'].nunique()}"
)

extra_model_pa = set(model_pa["record_key"]) - pa_keys

print(
    f"Final-model pseudo-absence keys NOT in authoritative "
    f"pseudo_absences_final: {len(extra_model_pa)}"
)

if extra_model_pa:
    print(sorted(extra_model_pa))


# ---------------------------------------------------------------------------
# 10. SAVE AUDIT
# ---------------------------------------------------------------------------

output = BASE / "pseudo_absence_record_lineage_audit.csv"

lineage.to_csv(
    output,
    index=False
)

print("\n" + "=" * 100)
print("AUDIT COMPLETE")
print("=" * 100)
print(f"Saved: {output}")

print("\nIMPORTANT:")
print("No source files were modified.")
print("Only the new audit CSV was created.")
print("=" * 100)
