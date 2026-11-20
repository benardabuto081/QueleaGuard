# Project Charter

> **Status: historical planning document (version 1).** Written at the start of the project and superseded by `docs/research_protocol_v2.md`, the frozen audit protocol and the audit synthesis (`docs/cv_audit_synthesis.md`). It is retained because the research record refers to it. Its scope, timeline and wording (for example "infestation risk") describe the original plan and are not current claims: the project models recorded occurrence and habitat suitability, not infestation or crop damage.

**Project Name:** QueleaGuard

**Project Title:** QueleaGuard: An AI-Based Early Warning System for Predicting Quelea Bird Infestation Risk in the Ahero Rice Irrigation Scheme and Surrounding Communities, Kisumu County, Kenya

**Version:** 1.1

**Status:** Planning

**Project Type:** Machine Learning | Geospatial Analytics | Environmental AI

**Team:**
- Bernard Abuto

**Repository:** QueleaGuard

> **Correction notice (v1.1):** The study area was originally scoped around two schemes, "Ahero" and "Nyamware." Research conducted during Milestone 2.1 established that Nyamware is a village/settlement adjacent to Ahero Irrigation Scheme, not a separate officially recognized irrigation scheme. This document reflects the corrected single-scheme study area. Full evidence and rationale: see docs/assumptions_and_decision_log.md, Log Entry 001.

---

# Executive Summary

QueleaGuard is an end-to-end machine learning project that aims to develop an intelligent early warning system capable of predicting the risk of Red-billed Quelea (*Quelea quelea*) bird infestations in the Ahero Rice Irrigation Scheme and its surrounding rice-growing communities in Kisumu County, Kenya.

The project addresses a persistent agricultural challenge affecting rice farmers, where seasonal invasions of quelea birds result in significant crop losses and reduced productivity. By integrating historical bird occurrence records with environmental, climatic, vegetation, and geospatial data, QueleaGuard seeks to generate predictive insights that support proactive pest management rather than reactive control.

QueleaGuard is designed as the foundation for a future agricultural decision-support platform that could evolve into a real-world solution for farmers and agricultural stakeholders.

---

# Vision

To leverage artificial intelligence and environmental data to improve agricultural resilience by enabling farmers to anticipate and mitigate crop losses caused by quelea bird infestations.

---

# Mission

To design, develop, and evaluate a reproducible machine learning system that predicts quelea infestation risk using open ecological, climatic, and geospatial datasets while adhering to best practices in data science, software engineering, and Responsible AI.

---

# Problem Statement

The Ahero Rice Irrigation Scheme, one of Kenya's most important rice-producing areas, and its surrounding rice-growing communities experience recurring losses due to seasonal invasions of Red-billed Quelea birds. Existing control strategies are predominantly reactive, relying on manual observation and emergency intervention after infestations have already begun.

Despite the availability of historical bird occurrence records and environmental datasets, there is currently no localized machine learning system that combines these data sources to estimate infestation risk before crop damage occurs.

This project seeks to address that gap by developing an interpretable predictive model capable of estimating infestation risk using historical bird observations and environmental conditions.

---

# Project Aim

To develop a machine learning-based early warning system capable of predicting the likelihood of Red-billed Quelea infestations in the Ahero Rice Irrigation Scheme and its surrounding communities using historical occurrence records and environmental data.

---

# Project Objectives

## Primary Objectives

- Construct a high-quality machine learning dataset by integrating multiple open datasets.
- Investigate the relationship between environmental conditions and quelea bird occurrences.
- Develop and evaluate predictive machine learning models for infestation risk.
- Identify the environmental factors that most influence infestation risk.
- Produce a reproducible and well-documented end-to-end machine learning workflow.

## Secondary Objectives

- Apply geospatial feature engineering techniques.
- Demonstrate best practices in Responsible AI.
- Produce professional technical documentation suitable for public GitHub repositories.
- Establish a foundation for future agricultural decision-support systems.

---

# Project Scope

### Included

- Historical quelea occurrence data
- Weather and climate data
- Vegetation indices
- Geospatial analysis
- Data engineering
- Exploratory Data Analysis
- Feature engineering
- Machine learning
- Model evaluation
- Explainability
- Responsible AI documentation

### Excluded

The following components are outside the scope of this phase of the project and are considered future work:

- Mobile application development
- SMS alert services
- Drone surveillance
- IoT sensor integration
- Real-time forecasting
- Cloud deployment
- Production APIs

---

# Expected Deliverables

- Project documentation
- Machine learning dataset
- Data dictionary
- Exploratory Data Analysis notebook
- Data preprocessing notebook
- Feature engineering notebook
- Model training notebook
- Model evaluation notebook
- Responsible AI report
- GitHub repository

---

# Success Criteria

The project will be considered successful if it:

- Produces a reliable and reproducible machine learning dataset.
- Demonstrates meaningful predictive performance using appropriate evaluation metrics.
- Identifies key environmental drivers of quelea infestations.
- Is fully documented, reproducible, and suitable for publication on GitHub.
- Demonstrates industry-standard project organization and documentation.

---

# Long-Term Vision

QueleaGuard is envisioned as the first iteration of an agricultural intelligence platform focused on protecting rice production through predictive analytics.

Future versions of the platform could integrate satellite imagery, real-time weather forecasts, farmer-reported sightings, drone surveillance, and mobile notification systems to provide operational early warning services for rice farmers across Kenya and eventually other regions affected by quelea bird infestations.

---

# Guiding Principles

The development of QueleaGuard will follow the following principles:

- **Scientific Integrity** — All methods and findings will be evidence-based and supported by credible data.
- **Reproducibility** — Every stage of the project should be repeatable using the documented workflow.
- **Transparency** — Assumptions, limitations, and design decisions will be clearly documented.
- **Responsible AI** — Ethical considerations, bias, and model limitations will be acknowledged and discussed.
- **Modularity** — Components should be organized for future extension and maintenance.
- **Documentation First** — Documentation will be treated as a core deliverable rather than an afterthought.
- **Real-World Relevance** — Technical decisions should prioritize practical agricultural impact while remaining achievable within the scope of the project.

---

> **Project Motto**
>
> *Predict Early. Protect Harvests.*
