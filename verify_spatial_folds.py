import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

dataset = pd.read_csv("data/processed/modelling_dataset_final.csv")
folds = pd.read_csv("data/processed/spatial_cv_folds.csv")

print("=== 1-2. Record coverage ===")
dataset_keys = set(dataset["record_key"])
fold_keys = set(folds["record_key"])
print(f"Modelling dataset records: {len(dataset_keys)}")
print(f"Fold file records: {len(fold_keys)}")
print(f"Fold file has duplicates: {folds['record_key'].duplicated().any()}")
print(f"Missing from fold file: {dataset_keys - fold_keys}")
print(f"Extra in fold file (not in dataset): {fold_keys - dataset_keys}")

print()
print("=== 3. Distinct fold IDs ===")
print(sorted(folds["fold"].unique()))

print()
print("=== 4. Class balance per fold ===")
merged = dataset[["record_key", "record_type"]].merge(folds, on="record_key")
balance = merged.groupby(["fold", "record_type"]).size().unstack(fill_value=0)
print(balance)
zero_class = ((balance["presence"] == 0) | (balance["pseudo_absence"] == 0)).any()
print(f"Any fold with zero presence or zero pseudo_absence: {zero_class}")

print()
print("=== 5. Reproducibility: re-run clustering independently, compare ===")
coords_df = dataset[["record_key", "record_type", "latitude", "longitude"]]
presence_coords = coords_df.loc[coords_df["record_type"] == "presence", ["latitude", "longitude"]].values
kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
kmeans.fit(presence_coords)
all_coords = coords_df[["latitude", "longitude"]].values
dists = np.linalg.norm(all_coords[:, None, :] - kmeans.cluster_centers_[None, :, :], axis=2)
recomputed_fold = dists.argmin(axis=1)
recomputed = pd.DataFrame({"record_key": coords_df["record_key"], "fold_recomputed": recomputed_fold})
check = folds.merge(recomputed, on="record_key")
mismatches = (check["fold"] != check["fold_recomputed"]).sum()
print(f"Mismatches between saved file and fresh re-run: {mismatches} of {len(check)}")

print()
print("=== 6. File currency vs dataset ===")
print(f"modelling_dataset_final.csv row count: {len(dataset)}")
print(f"spatial_cv_folds.csv row count: {len(folds)}")
print(f"record_key sets identical: {dataset_keys == fold_keys}")
