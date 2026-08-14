import pandas as pd

pseudo_path = "data/processed/pseudo_absences_final.csv"
model_path = "data/processed/modelling_dataset_final.csv"

pseudo = pd.read_csv(pseudo_path)
model = pd.read_csv(model_path)

print("\n=== CURRENT PSEUDO-ABSENCE FILE ===")
print(f"Records: {len(pseudo)}")
print(f"Unique keys: {pseudo['key'].nunique() if 'key' in pseudo.columns else 'NO key COLUMN'}")

print("\n=== MODELLING DATASET ===")
print(
    model["record_type"]
    .value_counts()
    .to_string()
)

print("\n=== PSEUDO RECORDS IN MODELLING DATASET ===")
model_pa = model[model["record_type"] == "pseudo_absence"].copy()
print(f"Records: {len(model_pa)}")
print(f"Unique keys: {model_pa['record_key'].nunique()}")

if "key" in pseudo.columns:
    pseudo_keys = set(pseudo["key"].astype(str))
    model_keys = set(model_pa["record_key"].astype(str))

    missing = pseudo_keys - model_keys
    present = pseudo_keys & model_keys

    print("\n=== KEY RECONCILIATION ===")
    print(f"Pseudo keys in source: {len(pseudo_keys)}")
    print(f"Pseudo keys in modelling dataset: {len(model_keys)}")
    print(f"Matched: {len(present)}")
    print(f"Missing from modelling dataset: {len(missing)}")

    if missing:
        print("\n=== MISSING PSEUDO-ABSENCE KEYS ===")
        print(sorted(missing))

        print("\n=== DETAILS OF MISSING RECORDS ===")
        cols = [
            c for c in [
                "key",
                "scientificName",
                "decimalLatitude",
                "decimalLongitude",
                "eventDate",
                "year",
                "grid_cell_id",
                "within_scheme_boundary"
            ]
            if c in pseudo.columns
        ]

        print(
            pseudo[
                pseudo["key"].astype(str).isin(missing)
            ][cols].to_string(index=False)
        )

print("\n=== MODELLING DATASET NULL AUDIT ===")
print(
    model.isna().sum()
    .sort_values(ascending=False)
    .to_string()
)

print("\n=== PSEUDO-ABSENCE NULL AUDIT ===")
print(
    pseudo.isna().sum()
    .sort_values(ascending=False)
    .to_string()
)
