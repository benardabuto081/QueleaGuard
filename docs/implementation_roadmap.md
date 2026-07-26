# Implementation Roadmap

**Project:** QueleaGuard

**Version:** 1.1

**Status:** Planning

> **Correction notice (v1.1):** Study area corrected from "Ahero and Nyamware" to "Ahero Irrigation Scheme and surrounding communities." See docs/assumptions_and_decision_log.md, Log Entry 001.

---

# 1. Purpose

This document defines the implementation strategy for QueleaGuard. It provides a structured execution plan covering project milestones, task breakdown, deliverables, quality assurance, collaboration workflow, and submission readiness.

The roadmap serves as the operational guide throughout the project lifecycle, ensuring that all technical, documentation, and capstone requirements are completed in a systematic and reproducible manner.

---

# 2. Project Timeline

| Phase | Duration | Status |
|---------|----------|--------|
| Project Planning | Week 1 | Complete |
| Data Acquisition | Week 1 | In Progress |
| Data Engineering | Week 2 | Planned |
| Exploratory Data Analysis | Week 2 | Planned |
| Feature Engineering | Week 3 | Planned |
| Machine Learning | Week 3 | Planned |
| Model Evaluation | Week 4 | Planned |
| Documentation | Week 4 | Planned |
| Final Presentation | Week 5 | Planned |

---

# 3. Project Milestones

## Milestone 1 - Project Foundation

Objectives

- Establish project documentation
- Create GitHub repository
- Define project architecture
- Finalize implementation roadmap

Deliverables

- Project Charter
- Project Specification
- Technical Architecture
- Data & Methodology
- Implementation Roadmap

Status: Complete (v1.1, corrected for the Ahero/Nyamware study area finding - see docs/assumptions_and_decision_log.md)

---

## Milestone 2 - Data Acquisition

Objectives

Acquire all required datasets.

Tasks

- Download GBIF records
- Acquire weather data
- Acquire vegetation data
- Acquire GIS datasets
- Review licensing
- Validate dataset quality

Deliverables

- Raw datasets
- Dataset inventory
- Source documentation

Status: In Progress. Milestone 2.1 (GBIF occurrence feasibility check) complete - see docs/dataset_feasibility_study.md, Section 9.

---

## Milestone 3 - Data Engineering

Objectives

Construct a machine-learning-ready dataset.

Tasks

- Clean datasets
- Remove duplicates
- Handle missing values
- Standardize coordinate systems
- Merge datasets
- Validate joins
- Export processed dataset

Deliverables

- Processed dataset
- Data dictionary
- Data validation report

---

## Milestone 4 - Exploratory Data Analysis

Objectives

Understand the data before modelling.

Tasks

- Distribution analysis
- Missing value analysis
- Spatial visualization
- Seasonal analysis
- Correlation analysis
- Outlier detection

Deliverables

- EDA Notebook
- Visualizations
- Initial findings

---

## Milestone 5 - Feature Engineering

Objectives

Generate meaningful predictive variables.

Tasks

- Environmental features
- Spatial features
- Temporal features
- Feature selection
- Feature validation

Deliverables

- Feature engineering notebook
- Final modelling dataset

---

## Milestone 6 - Machine Learning

Objectives

Develop predictive models.

Tasks

- Train baseline model
- Train advanced models
- Hyperparameter tuning
- Compare performance

Deliverables

- Trained models
- Performance comparison

---

## Milestone 7 - Model Evaluation

Objectives

Evaluate predictive performance.

Tasks

- Calculate evaluation metrics
- Error analysis
- Feature importance
- Explainability
- Responsible AI review

Deliverables

- Evaluation report
- Responsible AI Statement
- Model interpretation

---

## Milestone 8 - Project Completion

Objectives

Prepare the final project.

Tasks

- Final documentation
- Repository cleanup
- README completion
- Presentation slides
- Final review

Deliverables

- GitHub Repository
- Final Presentation
- Complete Capstone Submission

---

# 4. Work Breakdown Structure (WBS)

### Phase 1 - Planning

- Project documentation
- Repository setup
- Architecture design

### Phase 2 - Data

- Dataset acquisition
- Data cleaning
- Data integration

### Phase 3 - Analysis

- EDA
- Visualization
- Feature engineering

### Phase 4 - Modelling

- Baseline model
- Advanced models
- Hyperparameter tuning

### Phase 5 - Evaluation

- Metrics
- Explainability
- Responsible AI

### Phase 6 - Delivery

- Documentation
- Presentation
- GitHub publication

---

# 5. Team Responsibilities

## Bernard Abuto

Primary Responsibilities

- Project architecture
- Data engineering
- Geospatial processing
- Machine learning implementation
- GitHub management
- Technical documentation

---

## Faith Kipruto

Primary Responsibilities

- Literature review
- Data validation
- Exploratory data analysis
- Model evaluation
- Responsible AI documentation
- Presentation preparation

---

## Shared Responsibilities

- Dataset construction
- Feature engineering
- Model testing
- Weekly reviews
- Final presentation
- Report writing

---

# 6. GitHub Workflow

Repository Structure

main
|
+-- docs/
+-- data/
+-- notebooks/
+-- src/
+-- models/
+-- reports/
+-- presentation/
+-- README.md


Workflow

1. Plan
2. Implement
3. Test
4. Document
5. Commit
6. Review

Every major milestone should be committed with descriptive commit messages.

---

# 7. Quality Assurance Checklist

Before any task is considered complete, verify that:

- Documentation is updated.
- Code is reproducible.
- Outputs are validated.
- Visualizations are labelled.
- Data sources are cited.
- Notebook runs from start to finish without errors.
- Results are interpretable.

---

# 8. Risk Management

| Risk | Impact | Mitigation |
|--------|---------|------------|
| Limited bird observations | High | Combine multiple bird occurrence datasets |
| Missing environmental data | Medium | Use alternative open datasets |
| Class imbalance | High | Apply resampling or class weighting |
| Poor model performance | Medium | Compare multiple algorithms |
| Time constraints | Medium | Prioritize core deliverables before enhancements |
| Unverified assumptions about study area or data | High | Validate empirically before implementation - demonstrated in practice by the Milestone 2.1 Nyamware correction (see docs/assumptions_and_decision_log.md) |

---

# 9. Ngao Labs Submission Checklist

## Documentation

- [x] Project Charter
- [x] Project Specification
- [x] Technical Architecture
- [x] Data & Methodology
- [x] Implementation Roadmap
- [ ] README
- [x] Dataset Feasibility Study
- [x] Assumptions & Decision Log

---

## Data

- [ ] Dataset collected
- [ ] Dataset cleaned
- [ ] Data dictionary completed

---

## Machine Learning

- [ ] Baseline model
- [ ] Advanced model(s)
- [ ] Evaluation completed
- [ ] Error analysis completed
- [ ] Responsible AI statement completed

---

## GitHub

- [x] Repository organized
- [ ] Documentation complete
- [x] Requirements file added
- [x] License added
- [ ] Final commit completed

---

## Presentation

- [ ] Slides prepared
- [ ] Results summarized
- [ ] Demo tested
- [ ] Speaking notes prepared

---

# 10. Definition of Done

The project will be considered complete when:

- All Ngao Labs capstone requirements have been satisfied.
- Every notebook executes successfully from start to finish.
- The dataset is fully documented and reproducible.
- The repository follows a professional structure.
- All project documentation is complete.
- The README provides a clear entry point for users and recruiters.
- The project is ready to be showcased as a professional portfolio piece.

---

# 11. Future Roadmap

Following the successful completion of the capstone, QueleaGuard may evolve through the following phases:

### Phase 2 - Prototype

- Interactive risk prediction dashboard
- Model optimization
- Automated data update scripts

### Phase 3 - Pilot

- Integration of real-time weather forecasts
- Farmer-reported quelea sightings
- Validation with local agricultural stakeholders

### Phase 4 - Production

- REST API
- Web application
- Mobile application
- SMS alert service
- Cloud deployment
- Continuous model retraining

The long-term vision is to transform QueleaGuard into a scalable agricultural decision-support platform that helps protect rice production in Kenya and other regions affected by quelea bird infestations.

---

> **Project Motto**
>
> *Predict Early. Protect Harvests.*
