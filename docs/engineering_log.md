# QueleaGuard — Engineering Log

**Purpose:** Living engineering chronology for QueleaGuard. This document records what was done, what was discovered, why decisions were made, what artifacts were produced, and what remains unresolved. It complements `docs/assumptions_and_decision_log.md`, which remains the authoritative record for formal assumptions and decisions.

**Status legend:** `[VERIFIED]` confirmed by project artifacts/commits; `[LOCAL]` confirmed from the project owner's current working-tree output but not yet synchronized to GitHub; `[OPEN]` requires follow-up; `[SUPERSEDED]` retained for reproducibility but no longer current.

---

## Phase 2 — Data Acquisition & Methodological Foundation

### Milestone 2.1 — Occurrence Feasibility & Study-Area Correction `[VERIFIED]`

- Queried GBIF/eBird-derived occurrence data for *Quelea quelea* around Ahero/Kisumu.
- Obtained **161 raw occurrence records**.
- Investigated the original two-scheme framing and found that Nyamware should not be treated as a separate irrigation scheme.
- Corrected project geography to **Ahero Irrigation Scheme** with surrounding communities retained as contextual geography.
- The occurrence pull remained valid because it was geographic rather than scheme-name dependent.

**Key lesson:** project geography must be evidence-backed before downstream spatial modelling is built.

### Milestone 2.4 — Spatial Framework & Grain Size `[VERIFIED]`

- Rejected administrative/block polygons as the permanent modelling unit because authoritative sub-block geometries were unavailable and SDM precedent favors regular grids.
- Established three separate concepts:
  - **Study area:** Ahero Irrigation Scheme.
  - **Analysis extent:** Ahero + 50 km ecological buffer.
  - **Unit of analysis:** regular **5.5 km × 5.5 km grid cells**.
- 50 km buffer supported by quelea movement ecology, empirical occurrence coverage (85.1% of 161 records within 50 km), and environmental-data availability.
- Grain size selected through multi-factor reasoning: CHIRPS resolution, occurrence density, quelea movement scale, reproducibility, computational cost, and SDM precedent.

### Milestone 2.5 — Meteorology Source Decision `[VERIFIED]`

- Piloted NASA POWER and ERA5-Land.
- Selected **ERA5-Land** because its ~9 km resolution provides materially more spatial signal than NASA POWER's ~50–55 km resolution on the adopted 5.5 km grid.
- NASA POWER retained as a documented evaluated alternative rather than silently discarded.

### Milestone 2.6 — MODIS NDVI Pilot `[VERIFIED]`

- Confirmed AppEEARS access.
- Verified MODIS NDVI values and QA fields.
- Established that NDVI is feasible as a core environmental predictor.

### Milestone 2 Close `[VERIFIED]`

Data sources were piloted and the spatial framework/feature inventory were frozen before full extraction began.

---

## Phase 3 — Data Engineering

### Milestone 3.1 — Analysis Grid Generation `[VERIFIED]`

- Generated **328 grid cells** across Ahero + 50 km buffer.
- Grid generated at the adopted 5.5 km resolution.
- Only **4 cells** intersect the Ahero scheme boundary itself, establishing an important scale limitation: the scheme is smaller than one modelling cell.
- Artifact: `data/processed/analysis_grid.geojson`.
- Script: `src/generate_analysis_grid.py`.

### Milestone 3.2 — Occurrence-to-Grid Join `[VERIFIED]`

- **145/161** raw occurrence records matched the analysis grid.
- 16 records fell outside the analysis extent.
- `cell_0080` was found to contain a very high concentration of observations.
- Investigation showed the concentration represented repeated observations across many dates/observers at a persistent site, not simple duplicate rows.
- Local ecological knowledge was recorded separately rather than injected into modelling decisions.

### Milestone 3.3 — Temporal Feature Engineering Framework `[VERIFIED]`

Established variable-specific temporal representations:

- CHIRPS: 7-day, 30-day, and 90-day antecedent rainfall.
- MODIS NDVI: nearest valid 16-day composite plus seasonal anomaly.
- ERA5-Land: 7-day means plus same/nearest-day values.
- Terrain/hydrology: static features.

MODIS's temporal availability became the binding constraint for the feature-complete modelling dataset.

### Milestone 3.4 — CHIRPS Rainfall Extraction `[VERIFIED]`

- Initial live API approach failed; pipeline pivoted to local raster caching.
- Confirmed raw GDAL `/vsigzip/` reads work on the Windows/rasterio environment where higher-level gzip URI schemes failed.
- Extraction batched by date so each raster is opened once.
- **133/133** modelling-candidate presence records extracted successfully.
- Produced 7/30/90-day rainfall features.

### Milestone 3.5 — ERA5-Land Extraction `[VERIFIED]`

- Batched CDS requests by `(year, month)` rather than per record.
- Discovered CDS responses could arrive as ZIP archives despite requesting NetCDF; pipeline now detects archive signatures and extracts automatically.
- **133/133** modelling-candidate presence records extracted successfully.

### Milestone 3.6 — MODIS NDVI Extraction `[VERIFIED]`

- Batched extraction by spatial cell/task.
- Produced nearest-composite NDVI and seasonal anomaly features.
- Initial presence-side extraction reached **133/133** candidates.
- Later QA uncovered a quality-filter bug; see Milestones 3.10–3.11.

### Milestone 3.7 — Terrain Extraction `[VERIFIED]`

- Produced elevation and slope for **328/328** grid cells.
- Original SRTM/CGIAR-CSI access path was unavailable; the project pivoted to a maintained DEM source during implementation rather than fabricating missing terrain values.

### Milestone 3.8 — Hydrology Extraction `[VERIFIED]`

- Produced distance-to-water for **328/328** grid cells.
- Combined river/water context using HydroRIVERS/HydroSHEDS-derived data and Lake Victoria context.
- Earlier extraction evidence recorded approximately **684 river reaches** and median distance-to-water around **935 m**.

### Milestone 3.9 — Pseudo-Absence Methodology `[VERIFIED]`

Adopted **approximate Target-Group Background (TGB)** sampling using other-species GBIF bird records as an observer-effort proxy, combined with light spatial thinning.

Important methodological boundary:

> This is an approximation of full checklist-based TGB, not equivalent to eBird full-checklist TGB.

- Initial target ratio: approximately 1:1.
- Fixed random seed: `42`.
- A scheme-boundary gap was discovered: no effort-proxy records existed in the 4 Ahero boundary cells.
- Three alternatives were evaluated; the project retained uniform approximate TGB and documented the gap rather than introducing a special hybrid method that would reintroduce observer bias.

### Milestone 3.10 — Environmental Assembly & First Final Dataset `[SUPERSEDED]`

- Environmental layers were joined into a modelling table.
- Initial assembly reached **266 rows / 133 presence / 133 pseudo-absence**.
- Subsequent validation exposed two problems:
  1. MODIS fill-value handling could select `-3000` as a nearest composite.
  2. Three pseudo-absence records contradicted the TGB assumption by sharing a checklist/date/cell with a confirmed presence.
- Corrections removed these records and yielded the validated **259-row / 133:126** dataset.

The 266-row dataset remains useful as historical evidence but is not the current modelling dataset.

### Milestone 3.11 — NDVI & TGB Contradiction QA `[VERIFIED]`

- Corrected NDVI quality filtering so only good-quality composites are eligible for nearest-composite selection.
- Four pseudo-absence records in early 2000 had no valid prior MODIS composite and were excluded.
- Three pseudo-absence records sharing a confirmed target detection's checklist/date/cell were excluded.
- Final dataset after these corrections: **259 rows; 133 presence / 126 pseudo-absence**.
- Milestone 3 Data Engineering was formally closed at this point, but the later EDA cycle reopened the pseudo-absence pipeline after discovering a deeper temporal sampling problem.

---

## Phase 4 — EDA, Bias Discovery & Corrected Pseudo-Absence Pipeline

### Milestone 4.1–4.3 — Exploratory Data Analysis `[VERIFIED]`

EDA included descriptive statistics, correlations, spatial distributions, and temporal distributions. The critical discovery was severe pseudo-absence temporal concentration.

### Milestone 4.4 — Pseudo-Absence Month-Concentration Bug `[VERIFIED]`

**Problem:** 96.8% of the prior pseudo-absence sample fell in January/February, versus 20.3% of presences.

**Root cause:** the effort-pool script queried GBIF by year only with a 150-record/year cap. GBIF result ordering was not a safe temporal sampling mechanism, so several years became heavily or entirely January-weighted before the cap was reached.

**Correction:**
- Query explicitly by `(year, month)`.
- 16 years × 12 months = 192 targeted queries.
- New effort pool: **2,371 records**.
- Maximum monthly concentration reduced to about **8.8%**.
- Added pre-thinning exclusion of effort-proxy records sharing `(grid_cell_id, date)` with confirmed presences.
- Corrected pool passed month, year, cross-class contradiction, and spatial-coverage QC before environmental extraction resumed.

All v1 month-biased files were preserved as `*_v1_month_skewed.csv` and the corresponding modelling state remains recoverable through Git history.

### Post-4.4 Environmental Re-Extraction `[LOCAL]`

The project owner subsequently re-ran the environmental integration pipeline for the corrected pseudo-absence set. The current local audit reports:

- 133 pseudo-absence source records.
- 131 pseudo-absence rainfall feature rows.
- 133 pseudo-absence meteorology rows.
- 67 pseudo-absence NDVI feature rows plus an outstanding-cell manifest.
- Final assembled dataset: **259 rows**, with 133 presence / 126 pseudo-absence.
- Final modelling table has complete environmental features despite the intermediate feature-table counts being lower for some sources.

This state is currently **local evidence**, not yet fully synchronized to the GitHub repository.

---

## Milestone — Final Environmental Integrity Audit `[LOCAL]`

**Date:** 2026-08-14

The project owner ran `src/audit_environmental_integrity.py` locally.

### Passing checks

- 161 presence occurrence records; 161 unique keys.
- 133 pseudo-absence source records; 133 unique keys.
- 259 final modelling rows × 20 columns.
- 0 duplicate final rows.
- 0 duplicate final record keys.
- 0 missing values in the final modelling dataset.
- Rainfall: 259/259 complete.
- Meteorology: 259/259 complete.
- NDVI: 259/259 complete.
- Terrain: 259/259 complete.
- Hydrology: 259/259 complete.
- All configured feature-range sanity checks passed.
- Preliminary modelling-readiness checks passed.

### Warnings — NOT YET SIGNED OFF

1. **Observation-date provenance:** only 2/161 raw occurrence records have valid original dates, while 259/259 final modelling rows have dates. The assembly mechanism that produced the final dates must be traced.
2. **Temporal comparability:** the final audit still shows a January/February concentration for pseudo-absence dates despite the corrected effort-pool QC. This needs to be traced from corrected pool → sampled pseudo-absences → final assembly.
3. **Spatial concentration:** `cell_0080` contains up to 60 presence records and `cell_0156` up to 27 in the current audit. Random record-level splitting could leak site-specific information across train/test partitions.
4. **NDVI manifest:** 36 cells remain listed in `ndvi_missing_cells_manifest.csv`, while the final model has 100% NDVI completeness. The manifest's intended semantics must be explained.
5. **Repository synchronization:** the audit report and any post-commit data/code changes need to be committed before the current state is considered reproducible from `main`.

### Current gate

**Environmental feature completeness:** PASS.

**Scientific modelling readiness:** HOLD.

No modelling should begin solely because the completeness audit is green. The temporal provenance, corrected pseudo-absence sampling, NDVI manifest, and spatial-validation design must be reconciled first.

---

## Current Engineering State

### Confirmed foundations

- Study area and analysis extent defined.
- 5.5 km grid fixed.
- 328-cell spatial framework built.
- 145/161 occurrence records spatially matched.
- ERA5-Land selected over NASA POWER.
- CHIRPS rainfall extraction implemented.
- ERA5-Land extraction implemented.
- MODIS NDVI extraction implemented with quality filtering.
- Terrain and hydrology features complete for the grid.
- Approximate TGB pseudo-absence methodology selected and its major implementation bugs corrected.
- Environmental feature completeness passes on the current local final dataset.

### Immediate next work

1. Trace observation-date provenance in the final assembly pipeline.
2. Reproduce the corrected pseudo-absence month distribution from pool → sample → final model table.
3. Explain the 36-cell NDVI manifest and prove why final NDVI completeness is legitimate.
4. Quantify spatial clustering and define leakage-safe spatial cross-validation.
5. Re-run the complete integrity audit after those fixes/clarifications.
6. Only then freeze the modelling dataset and proceed to model development.

**Rule going forward:** every meaningful milestone must update this log and, where it changes methodology or a formal assumption, append to `docs/assumptions_and_decision_log.md` in the same work cycle.