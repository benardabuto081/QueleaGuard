# Technical Architecture

**Project:** QueleaGuard

**Version:** 1.1

**Status:** Planning

> **Correction notice (v1.1):** Study area corrected from "Ahero and Nyamware" to "Ahero Irrigation Scheme and surrounding communities." See docs/assumptions_and_decision_log.md, Log Entry 001.

---

# 1. Purpose

This document defines the technical architecture of QueleaGuard. It describes how data flows through the system, how datasets are constructed, how machine learning models are developed, and how predictions are generated.

The architecture prioritizes reproducibility, modularity, transparency, and maintainability while following industry best practices for machine learning projects.

---

# 2. Architecture Overview

QueleaGuard follows a layered architecture consisting of five major components:

1. Data Acquisition
2. Data Engineering
3. Machine Learning
4. Model Evaluation
5. Reporting & Documentation

The output of each layer becomes the input for the next layer, creating a fully reproducible end-to-end machine learning workflow.

---

# 3. High-Level System Architecture
                Open Data Sources
                       |
 +---------------------+---------------------+
 |                     |                     |
 |                     |                     |

GBIF / eBird CHIRPS / NASA MODIS / GIS
Bird Records Weather Data Vegetation & Maps
| | |
+---------------------+---------------------+
|
v
Data Acquisition Layer
|
v
Data Engineering Layer
(Cleaning . Validation . Integration)
|
v
Feature Engineering Layer
|
v
Machine Learning Pipeline
|
v
Model Evaluation Pipeline
|
v
Explainability & Responsible AI
|
v
Documentation & Final Deliverables


---

# 4. Data Acquisition Layer

The first layer collects all raw datasets required for model development.

### Bird Occurrence

Purpose

Historical Red-billed Quelea observations.

Potential Sources

- GBIF
- eBird

---

### Climate Data

Purpose

Capture weather conditions influencing bird movement.

Potential Sources

- CHIRPS
- NASA POWER

Variables

- Rainfall
- Temperature
- Relative Humidity
- Wind Speed

---

### Vegetation Data

Purpose

Estimate vegetation health and food availability.

Potential Sources

- MODIS NDVI
- Google Earth Engine

Variables

- NDVI
- Vegetation Index
- Vegetation Density

---

### Geospatial Data

Purpose

Describe landscape characteristics.

Variables

- Elevation
- Slope
- Distance to rivers
- Distance to wetlands
- Distance to permanent water bodies
- Land cover

---

# 5. Data Engineering Layer

The data engineering layer transforms raw datasets into a machine learning-ready dataset.

Major tasks include:

- Data cleaning
- Data validation
- Coordinate system standardization
- Spatial joins
- Temporal matching
- Feature extraction
- Missing value handling
- Dataset integration

Output

A unified structured dataset ready for analysis.

---

# 6. Exploratory Data Analysis Layer

This layer explores the integrated dataset before modelling.

Activities include:

- Missing value analysis
- Distribution analysis
- Class imbalance analysis
- Spatial visualization
- Seasonal trend analysis
- Correlation analysis
- Outlier detection

---

# 7. Feature Engineering Layer

New predictive variables will be generated from the raw data.

Examples include:

- Monthly rainfall totals
- Seasonal indicators
- Distance to nearest water body
- Vegetation trends
- Elevation categories
- Rolling weather statistics

The objective is to improve predictive performance while maintaining interpretability.

---

# 8. Machine Learning Layer

The modelling pipeline consists of several stages.

## Baseline Model

A simple classification model will first be trained to establish a performance benchmark.

Examples:

- Logistic Regression
- Decision Tree

---

## Candidate Models

More advanced algorithms will then be evaluated.

Potential models include:

- Random Forest
- Gradient Boosting
- XGBoost
- LightGBM (if appropriate)

The best-performing model will be selected based on predefined evaluation metrics.

---

# 9. Model Evaluation Layer

Model performance will be evaluated using multiple complementary metrics.

Primary Metrics

- F1 Score
- Precision
- Recall

Secondary Metrics

- ROC-AUC
- Confusion Matrix

Additional analyses

- Error analysis
- Feature importance
- Disaggregated evaluation by irrigation scheme sub-block (Ahero, Okana, Mbega, Kasiru/Kolal, Nokiso, Masune, Kobong'o), where applicable

---

# 10. Explainability Layer

To improve transparency and interpretability, the project will include explainability techniques such as:

- Feature Importance
- Permutation Importance
- SHAP (subject to project scope)

This will help explain why the model predicts higher infestation risk under certain environmental conditions.

---

# 11. Repository Architecture

QueleaGuard/

+-- docs/
+-- data/
| +-- raw/
| +-- interim/
| +-- processed/
| +-- external/
|
+-- notebooks/
| +-- 01_data_collection.ipynb
| +-- 02_eda.ipynb
| +-- 03_preprocessing.ipynb
| +-- 04_feature_engineering.ipynb
| +-- 05_model_training.ipynb
| +-- 06_model_evaluation.ipynb
|
+-- src/
+-- models/
+-- reports/
+-- presentation/
+-- requirements.txt
+-- README.md


---

# 12. Technology Stack

Programming Language

- Python

Development Environment

- Jupyter Notebook
- VS Code

Libraries

- Pandas
- NumPy
- Scikit-learn
- GeoPandas
- Rasterio
- XGBoost (if used)
- Matplotlib
- Seaborn
- SHAP

Version Control

- Git
- GitHub

---

# 13. Design Principles

The technical architecture follows the principles below:

- Modular design
- Reproducible workflows
- Open-source technologies
- Explainable machine learning
- Clear separation between data, modelling, and documentation
- Version-controlled development
- Maintainable project structure

---

# 14. Future Architecture

The current implementation represents a proof of concept.

Future versions of QueleaGuard may include:

- Satellite image ingestion
- Live weather forecasting
- Automated data pipelines
- REST API
- Web dashboard
- Mobile application
- SMS alert system
- Farmer-reported sightings
- Cloud deployment

These components are intentionally excluded from the capstone scope but define the long-term product vision.
