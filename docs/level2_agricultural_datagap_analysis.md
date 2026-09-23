# QueleaGuard Level 2 Agricultural Data-Gap Analysis
**Date:** 2026-08-15
**Status:** Investigation complete for initial pass. Supersedes the L2-RQ4/L2-RQ6 descope recommendation in `docs/research_protocol_v2.md` Part A/B - both are RETAINED per correction below. Authorizes NO new data acquisition or model training. Analysis and recommendation only.

---

## 0. Correction to v2.0

v2.0 recommended descoping L2-RQ4 (landscape structure) and L2-RQ6 (phenology) based on the current ~150-record interim dataset's sample size and an unverified assumption about RiceAtlas. Both grounds were premature: sample size is a property of today's interim dataset, not a fixed property of the research question, and "unverified" should have triggered investigation rather than a recommendation to drop. This document performs that investigation. Findings below change the picture substantially for both, and surface one urgent, previously unflagged issue (Section 1).

---

## 1. URGENT - Scheme Boundary Discrepancy (found during this investigation, not originally requested, but too consequential to hold back)

| | |
|---|---|
| Current project boundary | OSM polygon, 12.33 km² (~3,047 acres), used since Log Entry 001/002 |
| NIA current operational figure | 10,810 acres (~43.7 km²) - source: irrigationauthority.go.ke project page |
| NIA site-visit breakdown (Feb 2024) | 14,868 acres (~60.2 km²) across sub-blocks: Ahero-2,168, Okana-3,500, Mbega-800, Kasiru/Kolal-200, Nokiso-1,500, Masune-500, Kobong'o (remainder) |
| Implication | The OSM polygon likely captures only the core "Ahero" sub-block (~2,168 acres / 8.8 km² - roughly consistent with 12.33 km²), not the full multi-block scheme |

**Why this matters beyond Level 2:** the "4 of 328 grid cells intersect the scheme boundary" finding has been treated as an established fact since Log Entry 002 and was used to justify accepting the pseudo-absence scheme-boundary coverage gap in Log Entry 010. If the true operational footprint is 3.5-5x larger, substantially more grid cells likely intersect it, which could change that acceptance's reasoning (though probably not its bottom-line - see Section 6).

**No authoritative GIS shapefile was found via search** - NIA's web presence is informational/news, not an open-data portal. No canal/infrastructure vector data was found either (Section 5).

**Recommended action (investigation only, not yet executed):** attempt to digitize or approximate the full multi-block scheme boundary from satellite basemap imagery (Sentinel-2/Planet), using the sub-block names and acreages above as a guide, OR obtain higher-resolution cropland/rice classification (already-identified sources, Section 2) and treat contiguous rice-classified area near the known scheme centroid as an empirical boundary proxy rather than relying on the administrative polygon at all. This should be resolved before finalizing any irrigation-proximity feature (L2-RQ7) or reinterpreting Log Entry 010.

---

## 2. Rice Spatial Datasets (extent, boundaries, area/fraction, patch structure)

| Dataset | Purpose | RQ | Spatial res. | Temporal res. | Coverage | Historical range | License/access | Validation | Processing needed | Limitations | Suitable? |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Jiang et al. 2025, 20m Africa Rice Distribution Map | Rice extent/presence | L2-RQ1/2/3/5/7 | 20m | Single snapshot | Kenya confirmed included | 2023 only | Zenodo, CC-BY-4.0, no auth | ~1000 rice validation points/country per paper | Download, clip to extent, verify Ahero-area signal | Single-year; no direct historical match pre-2015 | **YES, primary source** |
| AFCD - Annual Africa Cropland Dataset | Generic (non-rice-specific) cropland extent, ANNUAL | Temporal-stationarity validation for the above | 30m | **Annual, 2000-2022** | Continent-wide | 2000-2022 | ESSD paper; Zenodo/GEE (access to be confirmed) | Accuracy 0.86±0.01 vs. independent samples; R²=0.86 vs FAO area estimates | Extract Ahero-area time series, cross-check against Jiang et al.'s 2023 rice mask | Not rice-specific - crop/non-crop only, can't distinguish rice from other crops in earlier years | **YES - use to empirically test the 2023-snapshot stationarity assumption, not just disclose it** |
| CROPGRIDS (Tang et al. 2023) | Independent rice-specific cross-check, coarse | Sanity-check for RQ1/2 | ~10km (5 arc-min) | Single/composite | Global | Not year-specific per source found | Open | Not verified in this pass | Coarse cross-check only | Matches existing 5.5km-ish grid scale, but far too coarse to be a primary source | Secondary/sanity-check only |
| SPAM2010 / SPAMAF2017 / GAEZ+2015 | Older crop-distribution models, cited as Jiang et al.'s comparison baselines | N/A | ~10km | Single year each | Africa-wide | 2010/2015/2017 | Open (IFPRI/GAEZ) | Established in prior literature | N/A | Same resolution problem as CROPGRIDS, and superseded in accuracy by Jiang et al. per that paper's own comparison | Not recommended - Jiang et al. 2025 is the better version of this same idea |
| Continent-wide multi-year field boundary labels (NICFI Planet basemap, 2017-2023, 4.8m) | Potential field-boundary source for L2-RQ4 | L2-RQ4 (secondary path) | 4.8m | 2017-2023, 6-monthly to monthly | Africa-wide **sample**, not exhaustive | 2017-2023 | Referenced in arXiv 2412.18483; access terms not yet confirmed | Used for ML training, not itself validated as ground truth | Would need confirmation the sample includes points near Ahero (not guaranteed - it's a sparse training sample, not full coverage) | Coverage near Ahero specifically unconfirmed | Backup only, not primary |
| "Delineate Anything" pretrained field-delineation model | Alternative field-boundary derivation | L2-RQ4 (secondary path) | Resolution-agnostic | N/A (model, not dataset) | Trained mostly on European fields | N/A | Open (arXiv 2504.02534, 2511.13417) | Explicit caveat: "transferability to sub-Saharan Africa smallholder systems requires further testing" | Would need to run the model ourselves on local imagery, then validate | Real risk of poor accuracy in African smallholder context per the authors' own stated limitation | Backup only, not primary |

**Revised L2-RQ4 assessment:** the primary path does not require any of the field-boundary datasets above. Landscape-configuration metrics (patch count, patch size distribution, edge density, nearest-neighbor distance between patches) can be computed directly from the Jiang et al. 2025 classified raster via standard connected-component/landscape-ecology analysis (e.g. `pylandstats`), without needing a separate field-boundary product. This was missed in v2.0's audit - I incorrectly treated this as requiring new data acquisition when it primarily requires additional *processing* of data already identified for RQ1/2/3. **RQ4 is feasible using already-identified data, contingent on the same raster-verification step already planned for RQ1/2/3 (Part E item 2, v2.0).**

## 3. Rice Temporal Datasets (multi-year extent, planting periods, calendars, phenology)

| Dataset | Purpose | RQ | Spatial res. | Temporal res. | Coverage | Historical range | License/access | Validation | Processing needed | Limitations | Suitable? |
|---|---|---|---|---|---|---|---|---|---|---|---|
| RiceAtlas (Laborte et al. 2017) | Admin-level crop calendar | L2-RQ6 (weak path) | Administrative unit, granularity for Kisumu unverified | One generic calendar per unit, not year-specific | Confirmed includes Kenya | N/A (static calendar) | Open, IRRI | Established literature | Verify Kisumu-level granularity | Likely reduces to a month-equivalent feature - see v2.0 concern, not yet resolved | Weak - only if genuinely below-national granularity confirmed |
| Sentinel-1 SAR backscatter time-series phenology (method, not dataset) | Genuine `location+date -> growth stage` estimation | L2-RQ6 (strong path) | Sentinel-1 native (~10m, resampled to analysis needs) | **Per-acquisition, ~6-12 day revisit** | Method demonstrated globally including a directly comparable East African case (Fogera, Ethiopia - tropical, lake-adjacent) | Sentinel-1 archive from 2014/2015 onward | Free (Copernicus/ASF), no auth for data; method requires implementation | Published accuracy ~70%+ in comparable studies (India, Ethiopia); NOT yet validated for Ahero specifically | **Substantial**: acquire raw Sentinel-1 GRD time series, implement backscatter-threshold classification (flooding dip / tillering rise / ripening shift) per published methodology (e.g. Yang et al. 2021 systematic method), validate against any available local crop-calendar ground truth | This is a real remote-sensing sub-project, not a data-gap checkbox - meaningfully larger scope than any other Level 2 item | **Feasible in principle, correctly scoped as a substantial task, not a quick win. Recommend treating as a distinct, separately-planned Level 2 milestone if pursued, not bundled into general Level 2 rollout.** |
| AFCD (same as Section 2) | Multi-year extent as a phenology *proxy floor* (crop present/absent by year, not stage) | Supports L2-RQ6 only indirectly | 30m | Annual | Continent-wide | 2000-2022 | Open | 0.86±0.01 | Same as Section 2 | Doesn't give stage, only presence/absence per year | Useful supporting evidence, not a phenology source itself |

**Revised L2-RQ6 assessment:** two genuinely distinct paths exist, not one weak option. **Path A (RiceAtlas)** remains as originally flagged - likely too coarse, still needs the granularity check. **Path B (Sentinel-1 SAR phenology)** is scientifically real and has a directly relevant East African precedent, but is honestly a much bigger undertaking than originally scoped - implementing a published method ourselves, not downloading a product. **Recommend: RETAIN CONDITIONALLY as stated, but explicitly split into "RQ6a - RiceAtlas administrative calendar" (cheap, likely weak) and "RQ6b - Sentinel-1 SAR-derived phenology" (expensive, potentially strong) as two separately-decidable sub-questions, rather than one RQ with one verdict.**

## 4. Rice Condition (NDVI/EVI time-series, rice-specific vegetation state)

Unchanged from v2.0 Part A (L2-RQ5): existing MODIS NDVI pipeline, masked to rice-classified pixels once the Section 2 raster is verified. No new findings this pass. Remains the highest-confidence, lowest-new-acquisition-cost Level 2 item, and the one most directly positioned to test the open H1.3 confound (NDVI's unexplained negative correlation with presence in Level 1 EDA).

## 5. Irrigation (scheme boundaries, canals, infrastructure, historical stability)

Covered by Section 1's urgent finding. **No canal/infrastructure vector data was located** via this search pass - genuinely appears to be a real gap, not something searched-past. NIA's public web presence is informational (news posts, project summaries) rather than an open-data portal. Options if this remains needed: (a) manual digitization from satellite basemap imagery, focused on the canal network visible in high-resolution imagery, (b) formal data request to NIA directly (outside this project's current scope/timeline), (c) proceed with scheme-boundary-proximity only (no canal-level detail) as a reduced-scope version of L2-RQ7, once Section 1's boundary discrepancy is resolved.

## 6. Quelea Observations/Background - Reassessment

No new findings this pass beyond what v2.0 Part D already established (background rice-representativeness check, sequenced after raster acquisition). One addition given Section 1's finding: the background-representativeness check should be run against the **corrected, full-extent** scheme boundary (once resolved), not the current possibly-undersized OSM polygon, since a check run against the wrong boundary would itself be unreliable.

## 7. Spatial Framework - Reassessment

v2.0 Part C's conclusion (5.5km appropriate for Level 1, point-buffer needed for Level 2) is **not contradicted** by anything found this pass, but Section 1's boundary finding means the specific numbers cited there (12.33 km² scheme vs. 30.25 km² cell) need to be revisited once the true scheme extent is confirmed - if the real scheme is ~44-60 km², it may actually span multiple grid cells more substantially than previously thought, which would partially (not fully) soften the "cell larger than scheme" problem, though the point-buffer recommendation for rice-specific variables likely still holds given rice cultivation is not perfectly commensurate with the wider grid regardless. **This should be re-run as a calculation, not assumed either way, once Section 1 resolves.**

## 8. Temporal Framework - Reassessment

No new findings this pass beyond v2.0 Part B.2 (temporal-subset definition, class-ratio tradeoff). The AFCD dataset (Section 2/3) adds a genuine new capability here: rather than a single blunt cutoff year, the Level-2-eligible subset could in principle be defined *per-record*, using AFCD's annual layer to check whether that specific record's cell was cropland in that specific year - a more precise, evidence-based inclusion rule than an arbitrary "2020-2026" window. Worth considering once AFCD access is confirmed, as a refinement to v2.0 Part B.2, not a replacement of the general approach.

---

## 9. Summary of Status Changes from v2.0

| Item | v2.0 status | Revised status | Why |
|---|---|---|---|
| L2-RQ4 (landscape structure) | Descope to future work | **RETAIN - feasible using already-identified data** | Raster-based patch metrics don't need a separate field-boundary dataset; v2.0 incorrectly assumed they did |
| L2-RQ6 (phenology) | Descope to future work | **RETAIN CONDITIONALLY, split into RQ6a (weak/cheap) and RQ6b (strong/expensive)** | Genuine SAR-based phenology method exists with a relevant regional precedent, not previously checked |
| Ahero scheme boundary | Treated as settled (12.33 km²) | **Under active question - likely undersized by 3.5-5x** | New finding this pass, not previously verified against NIA's own current figures |
| AFCD dataset | Not previously known | **New candidate source** - enables evidence-based (not just disclosed) testing of the rice-extent stationarity assumption | Found this pass |

**No new data acquisition, extraction, or model training has occurred.** This document is analysis and recommendation only, per your explicit instruction.
