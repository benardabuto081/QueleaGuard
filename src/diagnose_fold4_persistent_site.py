import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

NUMERIC_FEATURES = [
    "rice_pct_1000m", "dist_to_nearest_rice_m", "rainfall_30d",
    "temp_mean_7d", "dewpoint_mean_7d", "wind_mean_7d",
    "ndvi_nearest_composite", "elevation_m", "slope_deg", "dist_to_water_m",
]

df = pd.read_csv("data/processed/modelling_dataset_final.csv")
folds = pd.read_csv("data/processed/spatial_cv_folds.csv")
df = df.merge(folds, on="record_key")

season_dummies = pd.get_dummies(df["season"], prefix="season", drop_first=True)
X_full = pd.concat([df[NUMERIC_FEATURES], season_dummies], axis=1)
y_full = df["presence"].values
fold_ids = df["fold"].values

train, test = fold_ids != 4, fold_ids == 4
scaler = StandardScaler()
Xtr = np.hstack([scaler.fit_transform(X_full.loc[train, NUMERIC_FEATURES]), X_full.loc[train, season_dummies.columns].values])
Xte = np.hstack([scaler.transform(X_full.loc[test, NUMERIC_FEATURES]), X_full.loc[test, season_dummies.columns].values])
model = LogisticRegression(max_iter=1000, random_state=42).fit(Xtr, y_full[train])

fold4 = df[test].copy()
fold4["pred_proba"] = model.predict_proba(Xte)[:, 1]
fold4["in_cell_0080"] = fold4["grid_cell_id"] == "cell_0080"

summary = fold4.groupby(["in_cell_0080", "record_type"])["pred_proba"].agg(["count", "mean", "median", "min", "max"]).round(3)
print("Fold 4 predicted probability, split by cell_0080 membership and record type:")
print(summary)

fold4["pred_positive"] = fold4["pred_proba"] >= 0.5
print()
print("Fraction predicted positive at 0.5, same split:")
print(fold4.groupby(["in_cell_0080", "record_type"])["pred_positive"].mean().round(3))
