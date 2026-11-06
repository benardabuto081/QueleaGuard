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

print("fold | train_prev | test_prev | mean_pred_proba_on_test | frac_pred_positive_at_0.5")
for f in sorted(df["fold"].unique()):
    train, test = fold_ids != f, fold_ids == f
    scaler = StandardScaler()
    Xtr = np.hstack([scaler.fit_transform(X_full.loc[train, NUMERIC_FEATURES]), X_full.loc[train, season_dummies.columns].values])
    Xte = np.hstack([scaler.transform(X_full.loc[test, NUMERIC_FEATURES]), X_full.loc[test, season_dummies.columns].values])
    model = LogisticRegression(max_iter=1000, random_state=42).fit(Xtr, y_full[train])
    proba = model.predict_proba(Xte)[:, 1]
    print(f"  {f}  |   {y_full[train].mean():.3f}    |  {y_full[test].mean():.3f}   |        {proba.mean():.3f}            |        {(proba >= 0.5).mean():.3f}")
