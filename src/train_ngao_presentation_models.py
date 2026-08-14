"""
QueleaGuard — Emergency Presentation Model Training

TEMPORARY PRESENTATION ARTEFACT
--------------------------------
This training path exists only for the emergency presentation.

It is NOT the final QueleaGuard modelling pipeline.
The resulting models and metrics must be removed/replaced after
the presentation when the production environmental feature stack
has been fully validated.
"""

from pathlib import Path
import json

import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)


# ---------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------

DATA_PATH = Path("data/processed/emergency_presentation_dataset.csv")
OUTPUT_DIR = Path("models/emergency")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------------------

print("=" * 80)
print("QUELEAGUARD — EMERGENCY PRESENTATION MODEL TRAINING")
print("=" * 80)

print("\nWARNING:")
print("This is a TEMPORARY presentation modelling path.")
print("It is NOT the production QueleaGuard modelling pipeline.")

if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Emergency dataset not found: {DATA_PATH}"
    )

df = pd.read_csv(DATA_PATH)

print("\nDATASET")
print("-" * 80)
print(f"Path:   {DATA_PATH}")
print(f"Shape:  {df.shape}")


# ---------------------------------------------------------------------
# FEATURES
# ---------------------------------------------------------------------

TARGET = "presence"

FEATURES = [
    "rainfall_7d",
    "rainfall_30d",
    "rainfall_90d",
    "temp_mean_7d",
    "dewpoint_mean_7d",
    "wind_mean_7d",
    "temp_same_day",
    "dewpoint_same_day",
    "wind_same_day",
    "ndvi_nearest_composite",
    "ndvi_anomaly",
    "elevation_m",
    "slope_deg",
    "dist_to_water_m",
]

missing_columns = [
    column
    for column in FEATURES + [TARGET]
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Required columns missing from dataset: {missing_columns}"
    )

X = df[FEATURES].copy()
y = df[TARGET].astype(int)


# ---------------------------------------------------------------------
# DATA VALIDATION
# ---------------------------------------------------------------------

print("\nFEATURES")
print("-" * 80)

print(f"Number of features: {len(FEATURES)}")

for feature in FEATURES:
    print(f"  - {feature}")

print("\nCLASS DISTRIBUTION")
print("-" * 80)
print(y.value_counts().sort_index())

print("\nMISSING VALUES")
print("-" * 80)

missing_total = int(X.isna().sum().sum())
print(f"Total missing feature values: {missing_total}")

if missing_total:
    print("Missing values will be handled by the model pipeline.")


# ---------------------------------------------------------------------
# TRAIN / TEST SPLIT
# ---------------------------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

print("\nTRAIN / TEST SPLIT")
print("-" * 80)
print(f"Training records: {len(X_train)}")
print(f"Testing records:  {len(X_test)}")
print(f"Training class counts:\n{y_train.value_counts().sort_index()}")
print(f"Testing class counts:\n{y_test.value_counts().sort_index()}")


# ---------------------------------------------------------------------
# MODELS
# ---------------------------------------------------------------------

models = {
    "logistic_regression": Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            (
                "model",
                LogisticRegression(
                    max_iter=2000,
                    random_state=42,
                ),
            ),
        ]
    ),

    "random_forest": Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            (
                "model",
                RandomForestClassifier(
                    n_estimators=300,
                    max_depth=None,
                    min_samples_leaf=2,
                    random_state=42,
                    class_weight="balanced",
                    n_jobs=-1,
                ),
            ),
        ]
    ),
}


# ---------------------------------------------------------------------
# TRAIN + EVALUATE
# ---------------------------------------------------------------------

results = {}

print("\n")
print("=" * 80)
print("MODEL TRAINING")
print("=" * 80)

for model_name, model in models.items():

    print(f"\nTRAINING: {model_name}")
    print("-" * 80)

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": float(
            accuracy_score(y_test, predictions)
        ),
        "precision": float(
            precision_score(
                y_test,
                predictions,
                zero_division=0,
            )
        ),
        "recall": float(
            recall_score(
                y_test,
                predictions,
                zero_division=0,
            )
        ),
        "f1": float(
            f1_score(
                y_test,
                predictions,
                zero_division=0,
            )
        ),
        "roc_auc": float(
            roc_auc_score(
                y_test,
                probabilities,
            )
        ),
        "confusion_matrix": (
            confusion_matrix(
                y_test,
                predictions,
            ).tolist()
        ),
    }

    results[model_name] = metrics

    model_path = OUTPUT_DIR / f"{model_name}.joblib"

    joblib.dump(model, model_path)

    print(f"Saved: {model_path}")

    print(f"Accuracy:  {metrics['accuracy']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall:    {metrics['recall']:.4f}")
    print(f"F1:        {metrics['f1']:.4f}")
    print(f"ROC-AUC:   {metrics['roc_auc']:.4f}")
    print(
        f"Confusion matrix: "
        f"{metrics['confusion_matrix']}"
    )


# ---------------------------------------------------------------------
# SAVE METRICS
# ---------------------------------------------------------------------

results_payload = {
    "status": "TEMPORARY_PRESENTATION_MODEL",
    "dataset": str(DATA_PATH),
    "dataset_shape": list(df.shape),
    "training_records": int(len(X_train)),
    "testing_records": int(len(X_test)),
    "features": FEATURES,
    "random_state": 42,
    "test_size": 0.20,
    "models": results,
    "warning": (
        "These models are temporary presentation artefacts. "
        "They must not be treated as the final QueleaGuard "
        "production models."
    ),
}

metrics_path = OUTPUT_DIR / "emergency_model_metrics.json"

with open(metrics_path, "w", encoding="utf-8") as f:
    json.dump(
        results_payload,
        f,
        indent=2,
    )


# ---------------------------------------------------------------------
# FINAL SUMMARY
# ---------------------------------------------------------------------

print("\n")
print("=" * 80)
print("TRAINING COMPLETE")
print("=" * 80)

for model_name, metrics in results.items():
    print(
        f"\n{model_name.upper()}"
    )
    print(
        f"  Accuracy : {metrics['accuracy']:.4f}"
    )
    print(
        f"  Precision: {metrics['precision']:.4f}"
    )
    print(
        f"  Recall   : {metrics['recall']:.4f}"
    )
    print(
        f"  F1       : {metrics['f1']:.4f}"
    )
    print(
        f"  ROC-AUC  : {metrics['roc_auc']:.4f}"
    )

print("\nSaved model artefacts:")
print(f"  {OUTPUT_DIR / 'logistic_regression.joblib'}")
print(f"  {OUTPUT_DIR / 'random_forest.joblib'}")
print(f"  {metrics_path}")

print("\nREMINDER:")
print("These are emergency presentation models.")
print("The production QueleaGuard pipeline remains the source of truth.")

print("\n" + "=" * 80)
