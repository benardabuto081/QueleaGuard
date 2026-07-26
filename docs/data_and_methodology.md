# Data & Methodology

**Project:** QueleaGuard

**Version:** 1.1

**Status:** Planning

> **Correction notice (v1.1):** Study area corrected from "Ahero and Nyamware" to "Ahero Irrigation Scheme and surrounding communities." See docs/assumptions_and_decision_log.md, Log Entry 001.

---

# 1. Purpose

This document describes the methodology used to construct the QueleaGuard dataset, engineer predictive features, develop machine learning models, and evaluate model performance.

Since no existing dataset directly addresses quelea bird infestation prediction in the Ahero Irrigation Scheme and its surrounding communities, this project will construct a custom geospatial machine learning dataset by integrating multiple open datasets.

---

# 2. Research Methodology

The project follows the CRISP-DM (Cross-Industry Standard Process for Data Mining) framework.

The workflow consists of six phases:

1. Business Understanding
2. Data Understanding
3. Data Preparation
4. Modelling
5. Evaluation
6. Documentation & Reporting

---

# 3. Dataset Construction Strategy

Rather than relying on a single dataset, QueleaGuard will integrate multiple authoritative datasets to produce a unified machine learning dataset.

The integration process is the core innovation of this project.

---

# 4. Data Sources

## 4.1 Bird Occurrence Data

Purpose

Historical records of Red-billed Quelea observations.

Primary Sources

- Global Biodiversity Information Facility (GBIF)
- eBird (Cornell Lab of Ornithology)

Variables

- Observation ID
- Latitude
- Longitude
- Observation Date
- Species
- Coordinate Accuracy

These observations will form the basis for the target variable.

---

## 4.2 Climate Data

Purpose

Capture environmental conditions influencing quelea movement.

Potential Sources

- CHIRPS
- NASA POWER

Variables

- Rainfall
- Temperature
- Relative Humidity
- Wind Speed

---

## 4.3 Vegetation Data

Purpose

Estimate vegetation and crop conditions.

Potential Sources

- MODIS NDVI
- Google Earth Engine

Variables

- NDVI
- Vegetation Density
- Vegetation Anomaly

---

## 4.4 Geospatial Data

Purpose

Describe landscape characteristics.

Potential Sources

- OpenStreetMap
- Kenya Open GIS datasets
- HydroSHEDS
- SRTM DEM

Variables

- Elevation
- Slope
- Distance to rivers
- Distance to wetlands
- Distance to permanent water bodies
- Land cover

---

# 5. Study Area

The project focuses on:

- **Ahero Irrigation Scheme** - a single, NIA-administered, gazetted (4,176 acres) rice irrigation scheme established in 1966, in the Kano Plains near the lower basin of the Nyando River.
- Named sub-blocks within the scheme, including Ahero, Okana, Mbega, Kasiru/Kolal, Nokiso, Masune, and Kobong'o, used as the disaggregated evaluation unit (see Section 12).
- The surrounding rice-growing communities adjacent to the scheme, including Nyamware village.

Kisumu County, Kenya

This localized approach enables the model to capture environmental patterns specific to one of Kenya's most important rice-growing regions.

---

# 6. Dataset Integration Workflow

The final modelling dataset will be created through the following workflow:

Bird Occurrence Data
|
Weather Data
|
Vegetation Data
|
Geospatial Data
|
v
Coordinate Standardization
v
Spatial Matching
v
Temporal Matching
v
Feature Engineering
v
Integrated Dataset


---

# 7. Target Variable Construction

The project aims to predict **Quelea Infestation Risk**.

Two approaches will be considered depending on data availability:

## Option A: Binary Classification

- Infestation
- No Infestation

## Option B: Multi-Class Classification

- Low Risk
- Medium Risk
- High Risk

The final approach will be selected after exploratory analysis of the constructed dataset.

---

# 8. Feature Engineering

Features will be derived from environmental, spatial, and temporal data.

### Environmental

- Rainfall
- Temperature
- Relative Humidity
- Wind Speed

### Vegetation

- NDVI
- Vegetation Density
- Vegetation Change

### Spatial

- Latitude
- Longitude
- Elevation
- Slope
- Distance to River Nyando
- Distance to Wetlands

### Temporal

- Month
- Season
- Day of Year

---

# 9. Data Preprocessing

The preprocessing workflow will include:

- Removing duplicate records
- Handling missing values
- Standardizing coordinate systems
- Spatial joins
- Temporal alignment
- Feature scaling (where required)
- Encoding categorical variables
- Dataset validation

---

# 10. Exploratory Data Analysis

EDA will investigate:

- Missing values
- Class balance
- Spatial distribution
- Seasonal distribution
- Weather trends
- Vegetation trends
- Correlations
- Outliers

Visualizations will include:

- Histograms
- Boxplots
- Correlation heatmaps
- Geographic maps
- Time-series plots

---

# 11. Machine Learning Methodology

The project will compare multiple supervised learning algorithms.

Baseline Model

- Logistic Regression

Candidate Models

- Decision Tree
- Random Forest
- Gradient Boosting
- XGBoost (subject to feasibility)

Model selection will be based on performance, interpretability, and robustness.

---

# 12. Model Evaluation

Primary evaluation metrics:

- F1 Score
- Precision
- Recall

Secondary metrics:

- ROC-AUC
- Confusion Matrix

Additional analyses:

- Error Analysis
- Feature Importance
- Disaggregated Evaluation by irrigation scheme sub-block (Ahero, Okana, Mbega, Kasiru/Kolal, Nokiso, Masune, Kobong'o), if feasible - replacing the originally planned two-scheme disaggregation (see docs/assumptions_and_decision_log.md, Log Entry 001)

---

# 13. Responsible AI

The project will explicitly evaluate:

- Dataset bias
- Geographic bias
- Sampling bias
- Data quality limitations
- Model transparency
- Ethical considerations for agricultural decision support

A Responsible AI statement will be prepared as a required capstone deliverable.

---

# 14. Reproducibility

To ensure reproducibility, the project will:

- Use version control with Git.
- Maintain a documented project structure.
- Record preprocessing decisions.
- Document feature engineering steps.
- Specify library versions.
- Organize notebooks in execution order.
- Clearly cite all datasets and licenses.

---

# 15. Limitations

Potential limitations include:

- Sparse bird observations in some locations.
- Incomplete environmental records.
- Limited ground-truth infestation labels.
- Temporal gaps between datasets.
- Five-week implementation timeline.

These limitations will be acknowledged and discussed in the final report.
