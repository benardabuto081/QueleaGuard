# QueleaGuard Research Protocol v2.0 — Scientific Audit & Revision
**Date:** 2026-08-15
**Status:** Proposed revision, pending review/approval. v1.0 (docs/research_protocol.md) is preserved as a historical artifact and superseded by this document, per this project's established practice for versioned methodology documents (paralleling *_v1_month_skewed.csv precedent).
**Authorization:** This document authorizes NO new data acquisition. It is a design audit only.

---

## PART A — PER-RESEARCH-QUESTION AUDIT

Format per RQ: (1) Question (2) H1 (3) H0 (4) Target (5) Predictors (6) Spatial res. (7) Temporal res. (8) Available (9) Missing (10) Analysis (11) Validation (12) Confounders (13) Main limitation (14) Feasibility verdict.

### LEVEL 1 — QUELEA ECOLOGY

#### L1-RQ1 — Spatial distribution
1. How is Quelea occurrence distributed spatially across the 328-cell grid?
2. H1: Occurrence is spatially clustered (non-random hotspots exist).
3. H0: Occurrence is spatially random across cells (no significant clustering, e.g. Moran's I not significant).
4. Grid-cell presence count/density.
5. None (descriptive spatial statistics only); grid-cell centroids.
6. 5.5km (existing).
7. Not required (or time-sliced as a secondary analysis).
8. Fully available (occurrence-to-grid join complete).
9. None.
10. Kernel density estimation, Getis-Ord Gi* hotspot analysis, Moran's I.
11. N/A (descriptive).
12. **Observer-effort/accessibility bias** — raw presence density conflates true ecological hotspots with birding-site accessibility (already demonstrated: `cell_0080`). Must be interpreted relative to the effort-proxy pool's spatial density, not raw counts alone.
13. Presence-only data cannot distinguish "true hotspot" from "well-birded hotspot" without effort normalization.
14. **FEASIBLE**, contingent on effort-normalized interpretation (divide presence density by effort-pool density per cell, not raw counts).

#### L1-RQ2 — Environmental associations
1. Which environmental variables are associated with occurrence?
2. H1 (per-variable, as in v1.0 Section 4): rainfall+, elevation-, dist-to-water-, NDVI direction uncertain (see H1.3).
3. H0: No association between each variable and presence/background class membership.
4. Binary presence/pseudo-absence.
5. Rainfall (7/30/90d), temp/dewpoint/wind (7d+same-day), NDVI+anomaly, elevation, slope, dist-to-water.
6. Variable-specific (CHIRPS 5.5km, ERA5-Land 9km, NDVI 250m, SRTM 90m, hydrology vector) — already reconciled to record-level extraction.
7. Variable-specific per Log Entry 006 (daily / 16-day / static).
8. Fully available, QC-complete (133/133 all sources).
9. `month`/`season`/`day_of_year` (trivial, still not added).
10. Logistic Regression (baseline) + Random Forest/Gradient Boosting + SHAP; univariate presence-vs-background tests (Mann-Whitney) as EDA.
11. **Spatial CV — mandatory, not yet designed.**
12. **(a)** Multicollinearity: `rainfall_7d`/`30d` r=0.73, `temp_mean`/`same_day` r=0.88, `dewpoint_mean`/`same_day` r=0.91, `ndvi`/`anomaly` r=0.80 (already found in EDA). **(b) Geographic range mismatch**: pseudo-absence spans a far wider geographic envelope than presence (81 vs 20 unique cells; presence tightly clustered southwest, pseudo-absence spread to the buffer's edges — confirmed via spatial plot). This risks the model partly learning "is this near the tight presence cluster" rather than genuine habitat suitability — the single most important open confound from Level 1 EDA.
13. Presence-background (not presence-absence) design; association strength is relative to the background sample's geography, not an absolute occurrence-probability surface.
14. **FEASIBLE**, contingent on (a) multicollinearity handling in the baseline and (b) spatial CV fold design that explicitly tests generalization beyond the tight presence cluster, not just within it.

#### L1-RQ3 — Temporal dynamics
1. How does occurrence vary by month/season/year?
2. H1: Occurrence peaks in specific months aligned with post-rain vegetation flush (Cheke et al. 2007).
3. H0: No seasonal pattern in occurrence (uniform across months, relative to background).
4. Presence records' date distribution, **compared against the corrected background's date distribution**, not presence's raw distribution in isolation.
5. Month/season/day-of-year (missing, trivial to add).
6. N/A.
7. Monthly/seasonal binning.
8. Presence and (corrected) background dates both available.
9. `month`/`season` columns; a general regional bird-observation-effort time series (would fully deconfound "quelea seasonality" from "birder seasonality," but is not obtainable — mark as unattainable, not blocking).
10. Chi-square (presence vs. background month distribution), circular statistics for seasonality.
11. Temporal holdout (train earlier years, test later) is arguably as relevant here as spatial CV.
12. **Residual real-world observer-effort seasonality in presence records themselves** — the Log Entry 014 fix corrected the *background's* artificial retrieval-induced skew, but did not and cannot correct any genuine seasonal variation in real birding intensity that legitimately differs by month in the underlying eBird data. Month-stratified background retrieval equalizes the *comparison group's* construction bias, not the presence side's inherent real-world sampling pattern.
13. N is too thin for fine-grained (single-month) curve fitting (~11 presence records/month on average); only coarse (2-4 season) grouping is statistically supportable.
14. **FEASIBLE at coarse (seasonal) resolution only**; NOT feasible for fine month-by-month curve estimation given current N.

#### L1-RQ4 — Predictability
1. How well can spatial+environmental information estimate occurrence probability?
2. H1: Model achieves meaningfully better-than-baseline discrimination under spatial CV.
3. H0: Spatial-CV performance does not exceed a majority-class/climatology-only baseline.
4/5/6/7/8/9 — as L1-RQ2.
10. Nested CV with spatial blocking; bootstrap confidence intervals given small N.
11. **Spatial CV, mandatory — fold design not yet finalized (real open task).**
12. As L1-RQ2, plus: no pre-specified "meaningful improvement" threshold currently exists (flagged once already in the original Phase 1 review, never implemented — carried forward as a hard requirement here).
13. Small N (~260 records) limits power to detect anything but large effect sizes; wide bootstrap CIs expected.
14. **FEASIBLE**, contingent on defining the success threshold *before* seeing results (Section C.4).

#### L1-RQ5 — Variable importance
1. Which variables contribute most; are relationships linear or nonlinear?
2. H1: Elevation, distance-to-water, and rainfall dominate importance (per EDA correlation magnitudes).
3. H0: No variable materially outperforms others in importance (flat importance distribution).
4/5/6/7/8/9 — as L1-RQ2.
10. SHAP on the best-performing tree model; partial dependence plots for nonlinearity.
11. Same spatial CV scheme as L1-RQ4 (importance should be computed within CV, not on a single full-data fit).
12. SHAP importance is itself distorted by multicollinearity — correlated features (e.g. `temp_mean_7d` vs `temp_same_day`) split importance between them, understating their true combined relevance. Must either drop redundant features first or report grouped/aggregated importance.
13. Same as L1-RQ4.
14. **FEASIBLE**, contingent on resolving multicollinearity before interpretation, not after.

#### L1-RQ6 — Spatial generalization
1. Do relationships learned in observed locations generalize to spatially distinct locations?
2. H1: Performance degrades meaningfully under spatial CV relative to naive random CV (i.e., naive CV is optimistic).
3. H0: Spatial and random CV performance are statistically indistinguishable.
4-9 — as L1-RQ4.
10. Direct comparison: naive random K-fold vs. spatial-block K-fold, same model/features.
11. This RQ **is** the validation-strategy question — spatial CV is both method and object of study here.
12. Fold design risk: if a spatial fold happens to isolate an environmentally unique cluster (e.g. the `cell_0080` shoreline site), that fold could be artificially easy or hard independent of genuine generalization — fold design must check environmental representativeness per fold, not just spatial separation.
13. Only ~63 of 328 cells are used by any record at all — spatial folds will necessarily be small and cell-sparse; fold-level metric variance will likely be high.
14. **FEASIBLE**, and arguably the single most important L1 result to report honestly (with variance), given how directly it bears on every other RQ's validity.

---

### LEVEL 2 — QUELEA AND RICE AGRICULTURE

**Read Part B before this section — several Level 2 RQs below are marked infeasible or descoped as a direct result of that audit.**

#### L2-RQ1 — Rice presence & L2-RQ2 — Rice extent
1. Are occurrences associated with rice-growing cells/area; does rice-cover fraction affect occurrence probability?
2. H1: Higher rice-cover (point-buffer, not grid-cell — see Part B) is associated with higher occurrence probability.
3. H0: No association between local rice-cover and occurrence, after controlling for elevation/distance-to-water (which are themselves correlated with rice location).
4. Binary presence/background, **restricted to the Level-2-eligible temporal subset** (Part B.2).
5. Rice-cover fraction within a defined buffer radius of each record's point coordinates (not the 5.5km grid cell — see Part B.1).
6. 20m native (Jiang et al. 2025); aggregation radius TBD empirically (recommend testing 500m/1km/2km).
7. **Single snapshot, 2023.**
8. Rice raster confirmed to cover Kenya; not yet downloaded, clipped, or verified for the actual study area.
9. Direct verification that the raster shows meaningful (non-degenerate) variation within the analysis extent — this is data-gap action item #1, unperformed.
10. Logistic regression / tree model with rice-cover as an added feature to the L1 baseline; partial correlation controlling for elevation/dist-to-water.
11. Same spatial CV scheme as L1, applied to the restricted temporal subset.
12. **Elevation/distance-to-water confound** — rice cultivation in this landscape is itself constrained to low-lying, near-water land, meaning rice-cover will correlate with variables L1 already includes. Nested model comparison (M1 vs M3, Section C) is specifically designed to test whether rice adds *independent* information, not just re-detect the same lowland signal under a new name.
13. Class-ratio shift in the restricted subset (~92 presence : ~62 background, ~1.5:1, not the full dataset's near-balance) needs explicit handling (class weighting or accepting the imbalance with documented justification).
14. **FEASIBLE**, but strictly conditional on: (a) the raster verification step, (b) point-buffer (not grid-cell) computation, (c) explicit temporal-subset restriction with disclosed N reduction.

#### L2-RQ3 — Rice proximity
1. Does occurrence probability change with distance to nearest rice patch?
2. H1: Occurrence probability decreases with distance from rice.
3. H0: No relationship between distance-to-rice and occurrence.
4-9. Same as L2-RQ1/RQ2 (derived from the same raster).
10. Same as above, distance-to-nearest-rice as a continuous predictor.
11. Same.
12. Same elevation/water confound, plus: distance-to-rice will correlate with distance-to-water (already an L1 feature) for the same underlying landscape reason.
13. Same subset/N caveats.
14. **FEASIBLE**, same conditions as L2-RQ1/RQ2.

#### L2-RQ4 — Rice landscape structure (fragmentation/connectivity)
1. Does the spatial arrangement of rice fields matter?
2. H1: Higher rice-patch connectivity/lower fragmentation associates with occurrence.
3. H0: No relationship.
4-9. Same raster, plus a landscape-metrics computation step not yet built.
10. `landscapemetrics`-type tooling on the 20m raster.
11. Same.
12. Fragmentation metrics are sensitive to raster resolution/edge artifacts at aggregation boundaries; adds real methodological complexity.
13. **With an already-reduced Level-2-eligible N (~150 records), detecting subtle landscape-configuration effects — typically a secondary, smaller effect than raw extent/proximity in the SDM literature — is unlikely to be statistically well-supported.**
14. **NOT RECOMMENDED for the current phase.** Descope to explicit future work; revisit only if L2-RQ1-RQ3 show a strong-enough base rice signal to justify the added complexity.

#### L2-RQ5 — Rice condition (rice-masked NDVI)
1. Does rice-field vegetation state relate to occurrence?
2. H1: Occurrence associates with a specific NDVI range within rice-classified pixels (e.g. mid-growth greenness, not bare-soil or senescent).
3. H0: No relationship between rice-masked NDVI and occurrence, beyond what unmasked NDVI already shows.
4. Binary presence/background, temporal-subset restricted for the *mask definition* only.
5. Existing NDVI extraction (already temporally dynamic, matched per-record) masked to rice-classified pixels.
6. 250m NDVI x 20m rice mask.
7. **NDVI itself is per-record dynamic (16-day composite) — only the rice mask defining which pixels count is a 2023 snapshot.** This is a meaningfully lower temporal-risk construct than raw rice extent, because a formally gazetted, decades-old (est. 1966) irrigation scheme's footprint is plausibly the most stable rice landscape in the study area even if the specific map is dated.
8. NDVI pipeline exists; rice mask not yet obtained/verified.
9. Same raster verification step as L2-RQ1.
10. Compare rice-masked-NDVI vs. general NDVI as predictors, nested comparison.
11. Same spatial CV.
12. Same elevation/water confound as above, plus NDVI's own already-documented elevation confound (H1.3) — this RQ is a natural place to actually test H1.3 (whether presence's negative NDVI correlation reflects rice-paddy vegetation state rather than a general vegetation-avoidance signal).
13. Contingent entirely on the mask actually resolving the 4-8 scheme-adjacent cells at meaningful resolution — needs the verification step first.
14. **FEASIBLE, and higher-value than raw rice extent** given it directly tests the open H1.3 question. Recommend prioritizing this over L2-RQ1/RQ2 if time is constrained.

#### L2-RQ6 — Rice phenology
1. Are occurrences associated with particular crop-growth stages?
2. H1: Occurrence is more likely during grain-filling/ripening than land-preparation/early-vegetative stages.
3. H0: No association between crop stage and occurrence.
4/5. Binary presence/background; RiceAtlas-derived crop-stage label.
6. **Administrative-unit level (granularity for Kisumu/Kenya specifically unverified).**
7. Seasonal calendar, not year-specific — a single generic calendar applied across all 26 years of records, itself a strong stationarity assumption stacked on top of the rice-extent one.
8. RiceAtlas confirmed to include Kenya; exact spatial unit and calendar precision for this specific area **not verified**.
9. Direct confirmation of RiceAtlas's Kisumu-level granularity; without it, this variable cannot be responsibly constructed.
10. Would reduce to a categorical crop-stage feature if built.
11. Same spatial CV.
12. **This is the weakest Level 2 construct.** If RiceAtlas only provides one generic calendar per admin unit, "crop stage" for a given record reduces to a deterministic function of its month — meaning this variable would likely just re-encode the `month`/`season` feature already planned in L1-RQ3, under a different name, adding little independent information.
13. Granularity mismatch (admin-unit vs. grid-cell/record-level); circular risk with L1's own month feature.
14. **NOT RECOMMENDED for the current phase.** Mark explicitly as future work, contingent on locating a genuinely rice-specific (not just calendar-month-equivalent) phenology source. Do not build into the v2.0 committed scope.

#### L2-RQ7 — Irrigation
1. Does proximity to Ahero's irrigation infrastructure add explanatory value beyond generic rice presence?
2. H1: Proximity to the formal scheme boundary adds discrimination beyond rice-cover fraction alone.
3. H0: No additional discrimination beyond L2-RQ1-RQ3's rice variables.
4/5. Binary presence/background; distance to the existing Ahero OSM polygon (already in repo, Log Entry 001/002).
6. Vector-derived, already available.
7. **Static, but this is the most temporally defensible Level 2 construct** — infrastructure boundaries are far more stable over 26 years than which specific fields are actively cultivated in a given year.
8. **Fully available, no new acquisition needed.**
9. None.
10. Same nested-comparison approach.
11. Same spatial CV.
12. Resolution mismatch — only 4/328 cells intersect the scheme boundary itself, so this predictor has inherently low variance at 5.5km grain (same limitation already known from Log Entry 010's pseudo-absence coverage gap). Point-buffer computation (Part B.1) partially mitigates this by not discretizing to whole grid cells.
13. Low-variance predictor given the scheme's small footprint relative to even a point-buffer if the buffer is too large.
14. **FEASIBLE**, no acquisition blocker, cheapest Level 2 item to test first alongside L2-RQ5.

#### L2-RQ8 — Incremental predictive value
This is procedurally identical to the Level 3 nested-model comparison (Part C) and is not a separately feasible/infeasible question — it is answered *by* running M1 vs M3 (Section C), not by new data or method.

---

### LEVEL 3 — INTEGRATED MODEL

#### L3 (primary RQ)
1. Does integrating environmental and rice-agricultural information improve occurrence-probability estimation, and by how much?
2. H1 (H3.1 from v1.0): M3 outperforms M1 and M2 individually, but the marginal gain over M1 is modest given the elevation/water confound already flagged throughout Part A.
3. H0: M3's spatial-CV performance is not meaningfully better than M1's, per the pre-specified threshold (Section C.4).
4. Binary presence/background, Level-2-eligible temporal subset for any model including rice features (M2, M3, M4); full dataset for M0/M1.
5. Full nested feature sets per model (Section C.1).
6/7. Mixed spatial/temporal support across L1 (grid-cell-derived) and L2 (point-buffer-derived) features — **this mismatch must be explicitly resolved before M3/M4 are fit (Part B.1), not left implicit.**
8/9. As above — contingent on all Level 2 acquisition/verification steps.
10. Nested model family (M0-M4), spatial CV throughout, pre-specified improvement threshold per added layer.
11. Spatial CV, consistent fold assignment across all 5 models for fair comparison.
12. Cumulative confounders from Parts A/B: multicollinearity, geographic range mismatch, elevation/water/rice correlation, differing N per model (temporal-subset-restricted models have less data than M0/M1).
13. **The N-per-model inconsistency is a genuine analytical complication**: M0/M1 can use the full ~259-262 records, M2-M4 are restricted to the smaller Level-2-eligible subset. Comparing across models with different N requires care (e.g., also fitting M0/M1 on the *same restricted subset* as a fair comparison, in addition to the full-data version) — this should be built into the design now, not discovered during modelling.
14. **FEASIBLE**, contingent on everything above; recommend reporting two versions of M0/M1 (full-N and subset-matched) specifically to isolate whether Level 3's apparent gains are due to rice information or merely a different, smaller sample.

---

## PART B — LEVEL 2 CONSTRUCT-BY-CONSTRUCT FEASIBILITY VERDICT

| Construct | Temporal validity | Spatial resolution fit | Recommendation |
|---|---|---|---|
| Rice presence/extent | Single 2023 snapshot; pre-2015 fundamentally unattainable at this quality by any source (Sentinel-era ceiling) | 20m native; 5.5km grid dilutes signal badly (scheme < 1 cell) | **KEEP**, restricted to temporal subset, point-buffer computation |
| Rice proximity | Same as above | Same | **KEEP**, same conditions |
| Rice landscape structure | Same as above, plus added complexity | Resolution-sensitive metric computation | **DESCOPE** to future work — N too small to support |
| Rice condition (masked NDVI) | Better than raw extent — NDVI itself is dynamic; only the mask is static | 250m x 20m, feasible | **KEEP, prioritize** — directly tests the open H1.3 confound |
| Rice phenology | Admin-level calendar, likely month-equivalent, no year-specific data | Granularity unverified, likely too coarse | **DESCOPE** to future work — verify RiceAtlas granularity before ever reconsidering |
| Irrigation proximity | Most stable construct — infrastructure, not land-cover state | Already available, vector-based | **KEEP** — cheapest, least risky Level 2 item |
| Actual crop damage | No data source exists | N/A | **OUT OF SCOPE**, unchanged from Level 1's original guardrail |

### B.1 — Spatial support mismatch (grid-cell vs. point-buffer)

L1 features are grid-cell derived (5.5km). A 5.5km cell is larger than the entire Ahero scheme (30.25 km² vs 12.33 km²) — using the same grid for Level 2 rice variables would collapse most of the study area to near-zero rice-cover and produce a near-binary "in scheme or not" signal, largely redundant with the existing `within_scheme_boundary` flag. **Recommendation: compute Level 2 rice variables using a point-buffer around each record's actual coordinates** (candidate radii: 500m/1km/2km, to be tested empirically once the raster is available), not the grid cell. This creates a genuine mixed-support design for Level 3 (grid-cell L1 features + point-buffer L2 features) that must be explicitly justified in the eventual methodology write-up, not silently mixed. Alternative (recompute L1 features at point-buffer resolution too) is more internally consistent but would require re-extracting rainfall/NDVI/etc. at point rather than cell level — a substantial rework not currently recommended given L1 is already complete and validated at cell level; the mixed-support approach with explicit justification is the lower-cost, defensible path.

### B.2 — Temporal subset definition (recommended, not yet finalized)

Restricting to 2020-2026 (closest to the 2023 rice-map reference year) yields approximately:
- Presence: ~92 of 133 records (~69%)
- Pseudo-absence (v2, corrected): ~62 of 133 records (~47%)
- **Resulting class ratio ~1.5:1, not the full dataset's near-1:1** — must be handled explicitly (class weighting, or accept and document).

This range is a starting proposal, not a final decision — exact cutoff should be chosen jointly with the actual rice map's documented acquisition/validation date range once obtained, and sensitivity-tested (Section 12 of v1.0, retained here) against a tighter (e.g. 2021-2026) and looser (e.g. 2018-2026) window.

---

## PART C — GRID RESOLUTION AUDIT (5.5km)

| Use case | Verdict | Reasoning |
|---|---|---|
| Quelea observations (L1) | **Appropriate, unchanged** | Matches CHIRPS native resolution; finer grid would fragment already-sparse occurrence data (133 records across only 20-81 unique cells) into even sparser cells |
| Environmental predictors (L1) | **Appropriate, unchanged** | Grid was deliberately matched to the coarsest *necessary* covariate (CHIRPS); resampling logic (Log Entry 002) remains valid and is not affected by the Level 2 redesign |
| Rice data (L2) | **NOT appropriate as the primary computation unit** | Scheme footprint (12.33 km²) is smaller than one grid cell (30.25 km²); see Part B.1 |
| Integrated model (L3) | **Requires explicit mixed-support design** | Grid-cell L1 + point-buffer L2, justified rather than silently combined (Part B.1) |

**Verdict: the 5.5km grid remains correct for what it was originally designed for (Level 1) and should not be changed globally.** The redesign requires a *second*, finer spatial computation (point-buffer) specifically for Level 2 variables, not a wholesale regridding of the project.

---

## PART D — PSEUDO-ABSENCE / BACKGROUND STRATEGY AUDIT FOR LEVEL 2/3

**For Level 1 questions: no change required.** The approximate TGB methodology (Log Entry 009), month-stratified correction (Log Entry 014), and presence-conflict safeguard (Log Entry 013) remain the best available approach given no eBird EBD access and no true absence data — nothing about the Level 2 redesign invalidates this for Level 1's own questions.

**For Level 2/3 questions, one new, previously untested risk exists and must be checked before trusting any rice-related result:**

The background sample was constructed using *other bird species'* observation effort as a proxy — birders were not specifically visiting or avoiding rice fields; their observation targets are general birds. It is an open, currently unverified question whether the background sample's rice-cover distribution is representative of the study area as a whole, or systematically skewed relative to a true random background (e.g., if birders disproportionately visit lake-shoreline/wetland sites over rice-paddy interiors, or vice versa). If background points are *not* rice-representative, any rice-cover "association" found for Level 2 could partly reflect this sampling artifact rather than genuine quelea ecology — a Level-2-specific confound that Level 1 never needed to consider.

**Required new validation step (cannot be performed without the rice raster, so it is sequenced immediately after acquisition, before any Level 2 modelling):** compare the rice-cover distribution of (a) presence points, (b) background points, and (c) a spatially random sample of points across the analysis extent. If background and random-sample distributions are similar, the existing background is usable as-is for Level 2. If they diverge meaningfully, this becomes a new, explicitly documented limitation (following the Log Entry 010 precedent: investigate, evaluate options, document the resolution — not silently proceed).

**No change required to the pseudo-absence construction pipeline itself at this time** — this is a validation/interpretation step to add, not a resampling requirement, unless the check above reveals a real problem.

---

## PART E — REVISED DATA-GAP MATRIX

| # | Action | Blocks | Cost/Risk | Status |
|---|---|---|---|---|
| 1 | Download + clip Jiang et al. 2025 rice raster to analysis extent | All Level 2 RQs | Low (no auth, Zenodo, ~small file for one region) | Not started |
| 2 | Verify raster shows non-degenerate rice-cover variation in/near Ahero (empirical check, not assumed) | L2-RQ1/2/3/5/7 feasibility itself | Low (analysis only, no new download) | Not started |
| 3 | Run background-rice-representativeness check (Part D) | Validity of any Level 2 finding | Low (analysis only) | Not started, sequenced after #1-2 |
| 4 | Decide point-buffer radius (test 500m/1km/2km) | L2 feature construction | Low-medium (requires #1) | Not started |
| 5 | Define and sensitivity-test the Level-2-eligible temporal subset window | All Level 2 modelling | Low (analysis only) | Not started |
| 6 | Verify RiceAtlas's actual spatial granularity for Kisumu/Kenya | L2-RQ6 only | Low, but **do not proceed to acquisition even if positive** — RQ6 is descoped (Part A) pending a stronger justification than calendar-month-equivalence | Not started, low priority |
| 7 | Add `month`/`season`/`day_of_year` to the feature table | L1-RQ3, and needed regardless of Level 2 outcome | Trivial | Still not done since Milestone 3 |
| 8 | Design spatial CV fold scheme | L1-RQ4/5/6, all of Level 3 | Medium (real design work, not yet started) | Not started |
| 9 | Reassemble `modelling_dataset_final.csv` with corrected PA environmental data | Any Level 1 modelling | Low (script-ready, held pending this review) | Held per your instruction |

**Recommended sequencing if this protocol is approved:** items 7 (trivial) and 9 (already ready) can proceed immediately with no further review needed, as they're unaffected by anything in this audit. Items 1-2 (rice raster acquisition + verification) are the next real decision point — low-risk, and their result determines whether items 3-5 are worth pursuing at all.
