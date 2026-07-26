# Project Specification

**Project:** QueleaGuard

**Version:** 1.1

**Status:** Planning

> **Correction notice (v1.1):** Study area corrected from "Ahero and Nyamware" to "Ahero Irrigation Scheme and surrounding communities." See docs/assumptions_and_decision_log.md, Log Entry 001.

---

# 1. Introduction

This document defines the functional and technical specification of QueleaGuard. It describes what the project will accomplish, the machine learning problem being solved, the required datasets, expected outputs, system boundaries, and the technical deliverables.

This specification serves as the primary reference for implementation throughout the project lifecycle.

---

# 2. Project Overview

QueleaGuard is an end-to-end machine learning project that predicts the likelihood of Red-billed Quelea (Quelea quelea) bird infestations affecting rice farms within the Ahero Rice Irrigation Scheme and its surrounding rice-growing communities in Kisumu County, Kenya.

Rather than reacting after birds have invaded rice fields, the system aims to estimate infestation risk using historical bird occurrence records and environmental conditions.

The resulting predictive model will demonstrate how machine learning can support agricultural decision-making and provide a foundation for future early warning systems.

---

# 3. Research Question

Can historical bird occurrence records combined with environmental, climatic, vegetation, and geospatial variables be used to accurately predict the risk of Red-billed Quelea infestations in the Ahero Rice Irrigation Scheme and surrounding communities?

---

# 4. Machine Learning Problem

Problem Type:

**Supervised Machine Learning**

Learning Task:

**Classification**

Target Variable:

**Infestation Risk**

Possible classes:

- Low Risk
- Medium Risk
- High Risk

*(If the available data does not support three classes, the project will use a binary classification approach: Infestation / No Infestation.)*

---

# 5. Study Area

The study focuses on:

- **Ahero Irrigation Scheme** - a single, NIA-administered, gazetted (4,176 acres) rice irrigation scheme established in 1966, comprising named sub-blocks including Ahero, Okana, Mbega, Kasiru/Kolal, Nokiso, Masune, and Kobong'o.
- The surrounding rice-growing communities adjacent to the scheme, including Nyamware village, acknowledged as part of the broader agricultural and ecological context.

Location:

Kisumu County, Kenya

This localized scope allows the project to address a real agricultural challenge while maintaining a manageable dataset and implementation timeline.

---

# 6. Intended Users

The long-term users of QueleaGuard include:

- Rice farmers
- Agricultural extension officers
- Irrigation scheme managers
- County governments
- Agricultural researchers
- Food security organizations

---

# 7. Data Sources

The project will integrate multiple open datasets.

## Bird Occurrence

Purpose:

Historical records of Red-billed Quelea observations.

Potential Sources:

- GBIF
- eBird

---

## Weather Data

Purpose:

Environmental conditions influencing bird movement.

Potential Sources:

- CHIRPS
- NASA POWER

Variables may include:

- Rainfall
- Temperature
- Relative Humidity
- Wind Speed

---

## Vegetation Data

Purpose:

Estimate vegetation health and crop conditions.

Potential Sources:

- MODIS NDVI
- Google Earth Engine (if required)

Variables may include:

- NDVI
- Vegetation density
- Vegetation anomaly

---

## Geographic Data

Potential Sources:

Open GIS datasets

Variables may include:

- Elevation
- Slope
- Distance to rivers
- Distance to wetlands
- Distance to permanent water bodies

---

## Agricultural Data

Where available, additional variables may include:

- Rice growing season
- Irrigation blocks
- Land cover
- Crop calendars

---

# 8. Dataset Construction

Since no single dataset exists for this problem, the project will construct a new machine learning dataset by integrating multiple public datasets.

The process will include:

- Downloading source datasets
- Cleaning individual datasets
- Standardizing spatial reference systems
- Matching environmental conditions to bird observations by location and date
- Engineering predictive features
- Constructing the final modelling dataset

---

# 9. Expected Inputs

Examples of model inputs include:

- Latitude
- Longitude
- Month
- Rainfall
- Temperature
- Relative Humidity
- NDVI
- Elevation
- Distance to water
- Season
- Land cover

---

# 10. Expected Output

The model will produce an infestation risk prediction.

Possible outputs:

- Low Risk
- Medium Risk
- High Risk

or

- Infestation
- No Infestation

depending on the final dataset.

---

# 11. Technical Deliverables

The completed project will include:

- Clean machine learning dataset
- Data dictionary
- Exploratory Data Analysis
- Feature engineering workflow
- Baseline machine learning model
- Advanced machine learning model(s)
- Model evaluation
- Error analysis
- Explainability analysis
- Responsible AI assessment
- GitHub repository
- Technical presentation

---

# 12. Ngao Labs Capstone Requirements Mapping

The project will be developed to satisfy the official Ngao Labs Capstone requirements.

| Ngao Labs Requirement | QueleaGuard Deliverable |
|------------------------|-------------------------|
| Clearly defined problem statement | Project documentation |
| Well-documented dataset | Custom integrated dataset + Data Dictionary |
| Exploratory Data Analysis | EDA Notebook |
| Data preprocessing | Preprocessing Notebook |
| Feature engineering | Feature Engineering Workflow |
| Baseline model | Logistic Regression (or another appropriate baseline) |
| Advanced model(s) | Random Forest, Gradient Boosting, XGBoost (subject to experimentation) |
| Model evaluation using multiple metrics | Evaluation Notebook |
| Error analysis | Evaluation Report |
| Responsible AI Statement (500-700 words) | Responsible_AI.md |
| GitHub repository | Fully documented public repository |
| Presentation | Final capstone presentation |
| Reproducible workflow | Complete project documentation and notebooks |

**Additional Requirement:**
The project will also include **disaggregated evaluation by irrigation scheme sub-block** (e.g., Ahero, Okana, Mbega, Kasiru/Kolal, Nokiso, Masune, Kobong'o) if the dataset supports meaningful subgroup analysis. This replaces the originally planned two-scheme disaggregation following the Nyamware correction (see docs/assumptions_and_decision_log.md, Log Entry 001) and is a more accurate design, since these sub-blocks are real administratively-distinct units within the single confirmed scheme.

---

# 13. Assumptions

- Historical bird occurrence records are sufficient to build a proof-of-concept model.
- Environmental variables influence quelea movement.
- Public datasets are adequate for constructing a reproducible machine learning dataset.

---

# 14. Constraints

- Limited availability of localized infestation labels.
- Potential class imbalance.
- Data quality differences across multiple sources.
- Five-week implementation timeline.

---

# 15. Success Definition

The project will be considered successful if it:

- Meets all Ngao Labs Capstone requirements.
- Produces a reproducible machine learning workflow.
- Demonstrates meaningful predictive performance.
- Is well documented.
- Is suitable for inclusion in a professional GitHub portfolio.
- Serves as a strong showcase project for internships, research opportunities, and entry-level machine learning or data science roles.
