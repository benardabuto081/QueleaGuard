# QueleaGuard Research Protocol
**Version 1.0 — Draft for review**
**Date:** 2026-08-15
**Status:** Proposed. Requires review/approval before Level 2 data acquisition begins.

---

## 0. Purpose and Scope of This Document

This protocol formalizes the QueleaGuard research redesign following the Ngao Labs presentation. It supersedes the implicit single-level "environment -> occurrence" framing of the original Specification/Methodology documents, while preserving all completed Level 1 data engineering as the foundation of the new three-level architecture.

**This document does not authorize new data downloads.** It is a design and feasibility-gap document for review, per the instruction to design before acquiring.

---

## 1. Final Overarching Research Question

> How do spatial, environmental, temporal, and rice-agricultural conditions shape the occurrence of Red-billed Quelea (*Quelea quelea*) in and around rice-growing landscapes of the Ahero area, Kisumu County, Kenya, and can these relationships be used to estimate Quelea occurrence probability across the study region?

## 2. Overall Research Objective

To construct and evaluate a spatially and temporally explicit model of *Quelea quelea* occurrence probability that progressively incorporates environmental, then agricultural (rice), then integrated predictors — determining how much explanatory/predictive value each layer contributes, rather than assuming their combination is necessarily better.

## 3. Specific Objectives

1. Characterize the spatial, environmental, and temporal structure of confirmed Quelea occurrence (Level 1).
2. Determine whether rice-agricultural landscape variables provide explanatory information beyond general environmental conditions (Level 2).
3. Build and validate an integrated occurrence-probability model combining both layers (Level 3), using nested model comparison rather than a single all-variables model.
4. Establish a leakage-safe spatial validation methodology appropriate to the observed clustering in the occurrence data.
5. Produce a reproducible, provenance-documented dataset and pipeline suitable for publication.
6. Honestly characterize what the resulting model can and cannot claim (occurrence probability, not infestation or crop-damage risk, unless damage-observation data is later obtained).

---

## 4. Level 1 — Quelea Ecology: Research Questions

- **RQ1 (Spatial distribution):** How is Quelea occurrence distributed spatially across the 328-cell analysis grid? Are there hotspots, and are they consistent with known ecological features (e.g. `cell_0080`, Winam Gulf shoreline)?
- **RQ2 (Environmental associations):** Which environmental variables (rainfall at multiple lags, meteorology, NDVI, elevation, slope, distance to water) are associated with occurrence?
- **RQ3 (Temporal dynamics):** How does occurrence vary by month, season, and year? Does this align with the rainfall-driven breeding hypothesis (Cheke et al. 2007)?
- **RQ4 (Predictability):** How well can spatial + environmental information alone estimate occurrence probability, under leakage-safe validation?
- **RQ5 (Variable importance):** Which environmental variables contribute most (feature importance / SHAP), and are relationships linear or nonlinear?
- **RQ6 (Spatial generalization):** Do relationships learned in observed locations generalize to spatially distinct, unobserved locations?

### Level 1 Hypotheses

- **H1.1:** Occurrence probability increases with antecedent rainfall (30–90 day), consistent with vegetation-flush-driven breeding.
- **H1.2:** Occurrence probability decreases with elevation and distance to water, reflecting the lowland/lake-shoreline concentration already observed in EDA (Session findings: elevation r=-0.65, dist-to-water r=-0.42 vs. presence).
- **H1.3:** The NDVI relationship found in EDA (negative correlation with presence, r=-0.45) reflects a geographic confound with elevation/land-cover type rather than a direct ecological repellent effect, and requires explicit investigation rather than face-value interpretation once rice-landscape data is available (Level 2 may resolve this: quelea may prefer low-NDVI floodplain/rice-paddy over high-NDVI vegetated highland).
- **H1.4:** Naive random-split validation will substantially overstate model performance relative to spatially-blocked validation, given documented clustering (`cell_0080`, presence concentrated in 20 of 328 cells).

---

## 5. Level 2 — Quelea and Rice Agriculture: Research Questions

- **RQ1 (Rice presence):** Are Quelea occurrences spatially associated with rice-growing grid cells, versus non-rice cells at similar environmental values?
- **RQ2 (Rice extent):** Does proportion of rice cover within a grid cell affect occurrence probability?
- **RQ3 (Rice proximity):** Does occurrence probability change with distance from mapped rice fields?
- **RQ4 (Landscape configuration):** [Stretch — see limitations] Does rice patch fragmentation/connectivity matter?
- **RQ5 (Rice condition):** [Stretch, data-dependent] Does rice-field vegetation state (NDVI within rice-classified pixels specifically) relate to occurrence?
- **RQ6 (Rice phenology):** [Stretch, data-dependent] Are occurrences associated with particular crop-growth stages?
- **RQ7 (Irrigation):** Does proximity to the Ahero scheme's irrigation infrastructure add explanatory value beyond generic rice presence?
- **RQ8 (Incremental value):** Does adding rice/agricultural variables improve model performance over the Level 1 environmental-only baseline (nested model comparison, Section 9)?

### Level 2 Hypotheses

- **H2.1:** Grid cells with higher rice-cover fraction show higher occurrence probability than environmentally similar non-rice cells, reflecting the original agricultural-pest motivation for the project.
- **H2.2:** Rice-cover fraction and distance-to-water are correlated (rice is typically grown near water sources in this landscape), so Level 2 variables may show shared, not fully independent, explanatory power with Level 1 hydrology features — this must be tested (e.g. variance inflation, nested model comparison) rather than assumed additive.
- **H2.3 (provisional, contingent on RQ6 data availability):** Occurrence is more likely during grain-filling/ripening stages of the rice cycle than during land preparation or early vegetative stages, consistent with the agricultural-pest literature on quelea feeding behavior.

---

## 6. Level 3 — Integrated Model: Research Questions

- **RQ (primary):** Does integrating spatial, environmental, and rice-agricultural information improve estimation of Quelea occurrence probability, and by how much, over each layer alone?

### Nested model family (per handover specification)

| Model | Predictors |
|---|---|
| M0 | Spatial only (grid cell coordinates / spatial random effect) |
| M1 | Spatial + Environmental (current Level 1 feature set) |
| M2 | Spatial + Rice (Level 2 feature set) |
| M3 | Spatial + Environmental + Rice |
| M4 | Spatial + Environmental + Rice + Temporal (month/season) |

Comparison basis: spatially-validated F1/precision/recall/ROC-AUC per model, plus explicit likelihood-ratio or permutation-based tests of whether each added layer's improvement is meaningful relative to its added complexity — not raw metric comparison alone, given the small-N constraints already documented (259-262 records).

### Level 3 Hypotheses

- **H3.1:** M3 (Environmental + Rice) outperforms both M1 and M2 individually, but the marginal gain over M1 alone is modest given the likely correlation between rice-cover and existing hydrology/elevation features (see H2.2).
- **H3.2:** Spatial-only (M0) performance will be non-trivial given the documented spatial clustering, which is itself the reason spatial cross-validation (not naive random CV) is mandatory for honestly evaluating M1–M4 above it.

---

## 7. Target Variable Definition

**Unchanged from Level 1, explicitly re-affirmed, not re-opened without new evidence:**

- Target: binary Quelea **occurrence probability** (presence=1 vs. approximate Target-Group-Background pseudo-absence=0) per grid-cell/date record.
- **Not** infestation, **not** crop damage, **not** confirmed absence. This framing is unchanged from the existing project guardrail (Data & Methodology, "Engineering Decisions" table) and remains binding for all three levels.
- Presence records: GBIF/eBird-derived confirmed sightings, spatially joined to the 5.5km grid, temporally bounded to MODIS coverage (>=2000-02-18).
- Pseudo-absence records: approximate TGB sampling from other-species GBIF effort-proxy records, month-stratified (Log Entry 014), presence-conflict-safe (Log Entry 013/014), currently 133 records pending final reassembly with corrected environmental features.
- **Reassessment performed per this protocol's Section 13 instruction:** the existing methodology remains scientifically the best available approach given data constraints (no eBird EBD access, no true absence surveys). No superior alternative was identified during this redesign; the change here is contextual (situating it within Level 1) not methodological.

---

## 8. Candidate Predictor Variables — Full Table

| Variable | Why needed | RQ supported | Spatial res. | Temporal res. | Current availability | Source | Limitations |
|---|---|---|---|---|---|---|---|
| Rainfall 7/30/90d | Vegetation-flush/breeding driver | L1-RQ2, H1.1 | ~5.5km (CHIRPS native) | Daily | **Available** — 133/133 presence & PA extracted, QC-passed | CHIRPS v2.0 (local cache) | None significant |
| Temp/dewpoint/wind (7d mean, same-day) | Flight/activity conditions | L1-RQ2 | ~9km | Daily | **Available** — 133/133 both classes | ERA5-Land (CDS) | Coarser than CHIRPS |
| NDVI nearest composite + anomaly | Vegetation state/food availability | L1-RQ2, H1.3 | 250m | 16-day composite | **Available** — 133/133 both classes, quality-filtered (Task 190 fix) | MODIS MOD13Q1.061 (AppEEARS) | 16-day compositing limits precision; confounds with elevation per H1.3 |
| Elevation, slope | Terrain/roosting context | L1-RQ2 | 90m (SRTM) | Static | **Available** — all 328 cells | CGIAR-CSI SRTM | Static; no temporal dimension |
| Distance to water | Roosting/breeding proximity | L1-RQ2 | Vector-derived | Static | **Available** — all 328 cells | HydroRIVERS + OSM Lake Victoria | Static |
| Month / season / day-of-year | Temporal dynamics | L1-RQ3, L3-M4 | N/A | Per-record | **Gap** — flagged since Milestone 3, not yet added to feature table | Derivable from existing `observation_date` field | None significant — trivial to add |
| Rice presence/extent (binary or fraction per cell) | Core Level 2 driver | L2-RQ1, RQ2, H2.1 | 20m native, aggregate to 5.5km grid | Single snapshot, 2023 | **Available, unverified for study area** — needs direct download + clip to analysis extent | Jiang et al. 2025, 20m Africa Rice Distribution Map, Zenodo DOI 10.5281/zenodo.13729353, CC-BY-4.0 | Single-year (2023) snapshot applied across 2000-2026 occurrence period requires an explicit stationarity assumption; 20m->5.5km aggregation choice (binary threshold vs. fraction) needs justification |
| Distance to nearest rice patch | Proximity effect | L2-RQ3 | Derived from above | Static (2023 snapshot) | **Derivable** once rice raster is obtained and verified for study area | Derived from Jiang et al. 2025 | Same snapshot-year caveat as above |
| Rice patch fragmentation/connectivity metrics | Landscape configuration | L2-RQ4 | Derived from above | Static | **Stretch — not committed** | Derived, via `landscapemetrics`-type tooling | Adds complexity; only pursue if RQ1-RQ3 show meaningful rice signal first |
| Rice-field-specific NDVI/condition | Crop condition | L2-RQ5 | 250m (existing MODIS) x rice mask | 16-day | **Stretch — derivable** by masking existing NDVI extraction to rice-classified cells | Combination of existing NDVI pipeline + rice mask | Only meaningful once rice mask is verified at the Ahero scale (12.33 sq km scheme vs 20m pixels ~ feasible resolution match, unlike NDVI at 250m) |
| Rice crop-stage / phenology | Growth-stage alignment | L2-RQ6, H2.3 | Administrative unit (unconfirmed granularity for Kenya) | Seasonal | **Unconfirmed** — RiceAtlas (Laborte et al. 2017) confirmed to include Kenya at some administrative level; exact spatial unit for Kisumu/Ahero specifically not yet verified | RiceAtlas, IRRI (globally CC-licensed) | Administrative-level, not scheme-specific; may be too coarse to meaningfully align with grid-cell-level occurrence records |
| Irrigation infrastructure proximity | Level 2 RQ7 | L2-RQ7 | Ahero scheme boundary already held (OSM polygon, 12.33 sq km) | Static | **Available** — already in repo from Level 1 (Log Entry 001/002) | Existing OSM polygon | Only 4 grid cells intersect the scheme itself; limited discriminative power at 5.5km grain |
| Grid cell / spatial coordinates | Spatial baseline (M0) | L3 | 5.5km | Static | **Available** | Existing `analysis_grid.geojson` | None |

---

## 9. Statistical / ML Analysis Plan

1. **Baseline:** Logistic Regression, per-level (M0-M4), for interpretability and as the required floor comparison.
2. **Candidate models:** Random Forest, Gradient Boosting (XGBoost only if time/complexity justifies it — per existing project priority hierarchy, cut before core comparisons if constrained).
3. **Nested comparison (Section 6):** fit M0-M4 with identical validation scheme; report metric deltas with attention to the small-N regime (259-262 records) — treat marginal gains under ~262 records with appropriate skepticism, not as definitive.
4. **Explicit falsifiable success threshold** (per the original Phase 1 review's R7 recommendation, never actually implemented — carried forward here as a requirement): each added layer must be defined as "meaningfully improving" only if it beats the prior nested model by a pre-specified margin on the primary metric (e.g. F1), not any positive delta.

## 10. Validation Strategy

- **Spatial cross-validation is mandatory**, not optional, given documented clustering (Session finding: presence spans only 20 of 328 cells; up to 62 records historically in a single cell). Exact fold design (spatial block vs. grid-cell grouping vs. distance-based) is **not yet finalized** and must be designed against the actual spatial structure of the final Level 1+2 dataset once assembled — this is real, undone design work, not a formality.
- Primary metrics: F1, precision, recall. Secondary: ROC-AUC, confusion matrix.
- Disaggregated evaluation by spatial partition (not named sub-block, per Log Entry 002's established constraint).

## 11. Model Interpretation Strategy

- SHAP-based feature importance, per model in the nested family.
- Explicit cross-check of H1.3 (the NDVI/elevation confound) once Level 2 rice data is integrated — this is the single most important interpretive question raised by Level 1 EDA and should be foregrounded in reporting, not buried.
- Cross-reference against `docs/local_ecological_knowledge_and_hypotheses.md` (H1-H5) only after modelling, per the existing hard boundary (Log Entry 005) — unchanged by this redesign.

## 12. Sensitivity / Robustness Analyses

- Sensitivity of results to the 2023-snapshot rice-data stationarity assumption (Section 8) — e.g., restrict to a temporal subset of occurrence records closer to 2023 as a robustness check against the full 2000-2026 span.
- Sensitivity to pseudo-absence sampling (re-run with a different random seed as a robustness check, without changing the primary `random_state=42` result).

## 13. Limitations (to carry into all reporting)

- Presence-only, TGB-approximate pseudo-absence — not confirmed absence (unchanged, Part 9 of prior handover).
- Single-year rice snapshot applied across a 26-year occurrence window.
- Small-N regime (~260 records) limits statistical power for detecting genuinely small effect sizes, especially in the nested Level 3 comparison.
- Administrative-level (not scheme-specific) rice phenology data, if used, cannot resolve fine-grained crop-stage timing.
- Target remains occurrence probability, not infestation/damage risk.

## 14. Publication Outputs

Unchanged from existing Scientific Publication & Research Strategy: dataset (Zenodo/Figshare, deferred per Dataset Publication Strategy), paper (structure unchanged, Level 1/2/3 findings become Results subsections), GitHub repository.

## 15. Future Operational Application

Downstream early-warning/decision-support application remains explicitly a *potential future use*, contingent on what the research actually establishes — not assumed as a deliverable of this phase.

---

## 16. Data-Gap Summary (Action Items Before Level 2 Acquisition)

1. **Download and clip** the Jiang et al. 2025 rice raster to the existing 50km analysis extent — first real acquisition task, low-risk (no auth required, Zenodo).
2. **Verify RiceAtlas's actual spatial unit for Kisumu/Kenya** before committing to Level 2 RQ6.
3. **Decide binary vs. fractional rice-cover aggregation** to the 5.5km grid, with justification.
4. Add `month`/`season`/`day_of_year` to the feature table (trivial, already flagged since Milestone 3, still not done).
5. Design the spatial CV fold scheme against the actual assembled Level 1+2 dataset.

**Explicitly not started, per this protocol's own instruction:** any new download beyond the verification step above. Section 16 items are recommended next single tasks, in order, pending your review of this protocol.
