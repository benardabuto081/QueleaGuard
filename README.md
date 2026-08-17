# QueleaGuard

**AI/ML research project investigating the environmental, spatial, temporal, and rice-agricultural drivers of Red-billed Quelea (*Quelea quelea*) occurrence in and around the Ahero Rice Irrigation Scheme, Kisumu County, Kenya.**

[![Status](https://img.shields.io/badge/status-active%20research-yellow)]()
[![Python](https://img.shields.io/badge/python-3.x-blue)]()

> **Project Motto:** *Predict Early. Protect Harvests.*

---

## What QueleaGuard Is

Red-billed Quelea are one of the most numerous bird species on Earth and a major agricultural pest across sub-Saharan Africa. Farmers in Kenya's Ahero Irrigation Scheme currently rely on reactive control (scaring/culling after birds arrive) rather than any data-driven early warning.

QueleaGuard investigates whether historical bird occurrence records, combined with environmental (rainfall, meteorology, vegetation, terrain, hydrology) and rice-agricultural data, can estimate *Quelea quelea* occurrence probability across a defined analysis extent around Ahero.

**Important framing note:** this project models occurrence/habitat-suitability, not confirmed infestation or crop damage. The underlying data (GBIF/eBird) records where quelea have been seen, not where crop damage occurred. This distinction is treated as a hard scientific guardrail throughout the project - see `docs/assumptions_and_decision_log.md` and `docs/research_protocol_v2.md` for the full reasoning.

## Current Status

**This is an active research project, not a deployed system.** It began as a Ngao Labs Data Science & AI/ML Bootcamp capstone (presented successfully, August 2026) and has since been extended into a more ambitious, multi-level research architecture.

| Component | Status |
|---|---|
| Study area definition (Ahero scheme, 50km analysis extent, 5.5km grid) | Complete |
| Quelea occurrence data (GBIF/eBird, spatially matched) | Complete - 133 feature-complete presence records |
| Pseudo-absence / background methodology (approximate Target-Group Background) | Complete, QC-verified - 133 records, month-stratified, presence-conflict-safe |
| Environmental data (CHIRPS rainfall, ERA5-Land meteorology, MODIS NDVI, SRTM terrain, HydroRIVERS hydrology) | Complete and QC-verified for all records |
| Exploratory data analysis (Level 1) | In progress |
| Rice-agricultural data (Level 2) | Design/feasibility phase - see `docs/research_protocol_v2.md` |
| Model training and validation | Not yet started |
| Dataset and research publication | Planned, not yet started |

The project's Ngao Labs presentation used a snapshot dataset and model for demonstration purposes. **That presentation artifact is not the final research dataset or model** - see `docs/research_protocol_v2.md` for why, and for the current research architecture.

## Research Architecture

The project is organized into three progressively richer analytical levels:

1. **Level 1 - Quelea Ecology:** What spatial, environmental, and temporal conditions are associated with Quelea occurrence?
2. **Level 2 - Quelea & Rice Agriculture:** Does the rice-agricultural landscape add explanatory information beyond general environmental conditions?
3. **Level 3 - Integrated Model:** Does combining both improve occurrence estimation, and by how much?

Full research questions, hypotheses, feasibility audit, and data-gap analysis: [`docs/research_protocol_v2.md`](docs/research_protocol_v2.md).

## Documentation

| Document | Purpose |
|---|---|
| `docs/project_charter.md` | Vision, mission, scope |
| `docs/project_specification.md` | ML problem framing, deliverables |
| `docs/data_and_methodology.md` | CRISP-DM workflow, feature engineering |
| `docs/dataset_feasibility_study.md` | Per-source data catalogue and status |
| `docs/research_protocol_v2.md` | Current - three-level research architecture, per-RQ feasibility audit |
| `docs/assumptions_and_decision_log.md` | Numbered, chronological record of every methodological decision and its evidence (canonical source of truth) |
| `docs/local_ecological_knowledge_and_hypotheses.md` | Locally-sourced hypotheses, strictly separated from methodology |

## Data Sources

- **Occurrence:** GBIF (aggregating eBird and other sources)
- **Rainfall:** CHIRPS v2.0 (~5.5km)
- **Meteorology:** ERA5-Land (~9km), via Copernicus Climate Data Store
- **Vegetation:** MODIS NDVI (MOD13Q1.061, 250m), via NASA AppEEARS
- **Terrain:** CGIAR-CSI SRTM (90m)
- **Hydrology:** HydroRIVERS + OpenStreetMap (Lake Victoria)
- **Rice agriculture (proposed, Level 2):** Jiang et al. 2025, 20m Africa Rice Distribution Map (Zenodo, CC-BY-4.0)

## Repository Structure

```
QueleaGuard/
|-- docs/              Project documentation and decision log
|-- data/
|   |-- raw/           Raw GBIF pulls
|   |-- external/      Cached third-party rasters/vectors (git-ignored where large)
|   `-- processed/     Derived feature tables and assembled datasets
|-- src/               Pipeline scripts (data acquisition, extraction, validation, EDA)
|-- reports/           Milestone summaries and figures
|-- notebooks/         (planned)
`-- models/            (planned)
```

## Methodology Highlights

- **Presence-background, not presence-absence:** occurrence data is presence-only; absences are approximated via Target-Group Background sampling (other-species effort proxy), explicitly documented as an approximation, not equivalent to confirmed absence.
- **Evidence-first decision culture:** every non-trivial technical or methodological finding is logged with its evidence and reasoning before implementation, in `docs/assumptions_and_decision_log.md` (23+ entries as of the current phase).
- **Multiple corrected methodological bugs**, each documented rather than silently patched - including a severe temporal sampling bias in the original pseudo-absence pool (root-caused to undocumented GBIF API pagination behavior) and a MODIS fill-value quality-filtering bug in NDVI extraction.
- **Spatial cross-validation** is treated as mandatory, not optional, given documented spatial clustering in the occurrence data.

## Project Owner

- **Bernard Abuto** - data engineering, geospatial processing, ML implementation

## Status of This README

This README reflects the project's actual current state as of August 2026 and will be expanded (results, model performance, installation/usage guide, data dictionary, Responsible AI statement) as those become genuinely available - not before.

## License

TBD.
