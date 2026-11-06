"""
Baseline model: Logistic Regression, evaluated via leave-one-fold-out on
the 5 spatial CV folds (Log Entry 018). Predictor set per Log Entry 019.

Primary metrics: F1, Precision, Recall. Secondary: ROC-AUC, Confusion
Matrix (per Technical Architecture Section 9).
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix,
)

DATASET_PATH = "data/processed/modelling_dataset_final.csv"
FOLDS_PATH = "data/processed/spatial_cv_folds.csv"

NUMERIC_FEATURES = [
    "rice_pct_1000m", "dist_to_nearest_rice_m",
    "rainfall_30d",
    "temp_mean_7d", "dewpoint_mean_7d", "wind_mean_7d",
    "ndvi_nearest_composite",
    "elevation_m", "slope_deg", "dist_to_water_m",
]


def main():
    df = pd.read_csv(DATASET_PATH)
    folds = pd.read_csv(FOLDS_PATH)
    df = df.merge(folds, on="record_key")

    season_dummies = pd.get_dummies(df["season"], prefix="season", drop_first=True)
    feature_cols = NUMERIC_FEATURES + list(season_dummies.columns)
    X_full = pd.concat([df[NUMERIC_FEATURES], season_dummies], axis=1)
    y_full = df["presence"].values
    fold_ids = df["fold"].values

    print(f"Feature set ({len(feature_cols)} columns): {feature_cols}\n")

    results = []
    for test_fold in sorted(df["fold"].unique()):
        train_mask = fold_ids != test_fold
        test_mask = fold_ids == test_fold

        X_train, X_test = X_full[train_mask], X_full[test_mask]
        y_train, y_test = y_full[train_mask], y_full[test_mask]

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train[NUMERIC_FEATURES])
        X_test_scaled = scaler.transform(X_test[NUMERIC_FEATURES])

        X_train_final = np.hstack([X_train_scaled, X_train[season_dummies.columns].values])
        X_test_final = np.hstack([X_test_scaled, X_test[season_dummies.columns].values])

        model = LogisticRegression(max_iter=1000, random_state=42)
        model.fit(X_train_final, y_train)

        y_pred = model.predict(X_test_final)
        y_proba = model.predict_proba(X_test_final)[:, 1]

        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        try:
            auc = roc_auc_score(y_test, y_proba)
        except ValueError:
            auc = np.nan
        cm = confusion_matrix(y_test, y_pred)

        results.append({
            "fold": test_fold, "n_test": len(y_test),
            "n_presence_test": int(y_test.sum()),
            "precision": precision, "recall": recall, "f1": f1, "roc_auc": auc,
        })
        print(f"--- Fold {test_fold} (n={len(y_test)}, {int(y_test.sum())} presence) ---")
        print(f"Precision: {precision:.3f}, Recall: {recall:.3f}, F1: {f1:.3f}, ROC-AUC: {auc:.3f}")
        print(f"Confusion matrix:\n{cm}\n")

    results_df = pd.DataFrame(results)
    results_df.to_csv("reports/baseline_logistic_regression_cv_results.csv", index=False)

    print("=== Aggregate across 5 folds ===")
    for metric in ["precision", "recall", "f1", "roc_auc"]:
        print(f"{metric}: mean={results_df[metric].mean():.3f}, std={results_df[metric].std():.3f}")


if __name__ == "__main__":
    main()
