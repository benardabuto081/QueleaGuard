"""
Spatial cross-validation fold assignment, v2: cluster centroids derived
from PRESENCE coordinates only, then assign every point (presence and
pseudo-absence) to its nearest presence-derived centroid.

v1 (clustering on all points) produced a fold with zero presence records
(pure background, unusable for evaluation) - see fold-balance check before
this revision. Clustering on presence locations specifically guarantees
every fold is anchored on a real presence cluster.

Methodology: Roberts et al. 2017, Ecography 40(8):913-929; Valavi et al.
2019, Methods Ecol Evol 10(2):225-232.

Output: data/processed/spatial_cv_folds.csv (record_key, fold)
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

INPUT_PATH = "data/processed/modelling_dataset_final.csv"
OUTPUT_PATH = "data/processed/spatial_cv_folds.csv"
N_FOLDS = 5
SEED = 42


def main():
    df = pd.read_csv(INPUT_PATH)[["record_key", "record_type", "latitude", "longitude"]]

    presence_coords = df.loc[df["record_type"] == "presence", ["latitude", "longitude"]].values
    kmeans = KMeans(n_clusters=N_FOLDS, random_state=SEED, n_init=10)
    kmeans.fit(presence_coords)

    all_coords = df[["latitude", "longitude"]].values
    dists = np.linalg.norm(all_coords[:, None, :] - kmeans.cluster_centers_[None, :, :], axis=2)
    df["fold"] = dists.argmin(axis=1)

    df[["record_key", "fold"]].to_csv(OUTPUT_PATH, index=False)
    print(f"Saved to {OUTPUT_PATH}")

    print("\nFold sizes and class balance:")
    print(df.groupby(["fold", "record_type"]).size().unstack(fill_value=0))

    print("\nFold centroid locations (derived from presence points):")
    for i, (lat, lon) in enumerate(kmeans.cluster_centers_):
        n = (df["fold"] == i).sum()
        print(f"  Fold {i}: centroid ({lat:.4f}, {lon:.4f}), n={n}")


if __name__ == "__main__":
    main()
