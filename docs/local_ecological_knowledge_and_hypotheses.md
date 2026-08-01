# Local Ecological Knowledge & Hypotheses

**Project:** QueleaGuard
**Status:** Living document - qualitative knowledge source, separate from project methodology
**Related:** docs/assumptions_and_decision_log.md, Log Entry 004 and Log Entry 005

---

# 1. Purpose and Epistemic Status

This document records local ecological knowledge (LEK) relevant to QueleaGuard, contributed by the project owner, and derives explicit, testable hypotheses from it.

**This is not evidence, and it is not project methodology.** It is a qualitative knowledge source, distinct in kind from the peer-reviewed literature, empirical data, and authoritative sources used elsewhere in this project. Its role is limited strictly to hypothesis generation. Hypotheses derived here are checked against model outputs and data patterns after the fact - they do not inform feature engineering, pseudo-absence generation, model tuning, or validation at any stage. See Section 4 for an explicit statement of this boundary.

Recording LEK transparently, with clear attribution and clear epistemic boundaries, is consistent with this project's Responsible AI principles: it makes a real knowledge input visible and checkable, rather than either discarding it or letting it silently shape results.

---

# 2. Recorded Knowledge

## 2.1 Personal Observation

The project owner (Bernard Abuto) grew up near the Ahero Irrigation Scheme, in the area locally known as Nyamware (the same area addressed in Log Entry 001 - confirmed not to be an officially recognized irrigation scheme, but a village/settlement adjacent to Ahero). From personal experience growing up in this area, quelea are widely regarded locally as a significant, recurring problem affecting rice farming in this vicinity.

## 2.2 Community-Reported Knowledge (Secondhand, Not Independently Verified)

Separately, and reported here as secondhand community knowledge rather than personal observation, local farmers and residents have described:

- A commonly-repeated account that large quelea flocks roost in trees along the Lake Victoria / Winam Gulf shoreline, and fly eastward at dawn into rice-growing areas (including, in this account, the Nyamware area specifically) to feed.
- A general understanding among older farmers that the area sits within a low-lying floodplain historically connected to the Lake Victoria basin, and recollections of flooding in nearby rice fields during years of high Lake Victoria water levels.

**Important qualification on Nyamware specifically:** its precise location, extent, and relationship to the Ahero scheme have not been independently verified by this project (see Log Entry 001 - OpenStreetMap and authoritative NIA sources do not resolve this). That Nyamware is "one of the areas most affected by quelea" is recorded here strictly as a locally-held belief the project owner is personally aware of, not as a confirmed fact, and not as a claim this project can currently locate precisely enough to test as a place-specific hypothesis. It is retained in this document for completeness and possible future investigation, not as a current basis for any spatial claim.

---

# 3. Derived Hypotheses (Testable Against Project Datasets)

These hypotheses are phrased so they can be checked against data and model outputs already planned for this project (GBIF/eBird occurrence, CHIRPS rainfall, ERA5-Land meteorology, MODIS NDVI, SRTM elevation, HydroSHEDS hydrology), once those outputs exist. None of them are assumed true; they are recorded now, before modelling, specifically so later comparison is not influenced by hindsight.

**H1 - Shoreline proximity and occurrence probability.** Grid cells nearer to the Lake Victoria / Winam Gulf shoreline will show higher predicted occurrence probability than equally-distant cells in other directions from Ahero, after controlling for rainfall and NDVI. *Testable against:* HydroSHEDS distance-to-water feature, final model's per-cell predicted probabilities.

**H2 - Elevation and flood-proneness correlation with occurrence.** Lower-elevation grid cells within the analysis extent (consistent with floodplain characteristics) will show higher occurrence probability than higher-elevation cells, independent of distance to water alone. *Testable against:* SRTM elevation feature, final model's feature importance / partial dependence for elevation.

**H3 - Rainfall-vegetation-occurrence chain near the shoreline.** The known ecological mechanism (rainfall triggers vegetation flush, which drives quelea breeding/foraging - Cheke et al. 2007) should be independently detectable in the shoreline-proximate cells specifically, i.e., NDVI and antecedent rainfall should both be elevated in high-occurrence-probability cells near the lake, not just correlated with occurrence generally across the whole extent. *Testable against:* CHIRPS rainfall features, MODIS NDVI features, spatial pattern of model predictions.

**H4 - Persistent site consistency over time.** If cell_0080 (Log Entry 004) reflects a genuinely persistent ecological feature rather than sporadic sightings, occurrence-associated environmental conditions (rainfall, NDVI) at that cell across different years should show a recognizable seasonal pattern, rather than appearing random. *Testable against:* CHIRPS/MODIS time series extracted specifically for cell_0080, once Milestone 3's environmental extraction is complete.

**H5 - Meteorological plausibility of a dawn roost-to-feed commute (if timestamp data supports it).** If eBird checklist records include time-of-day information, sightings near the shoreline should skew toward early morning hours more than sightings elsewhere in the analysis extent, consistent with the reported dawn-departure account. *Testable against:* eBird EBD checklist timestamps, if/when EBD access is pursued (Dataset Feasibility Study, Section 2.1) - not testable with the current GBIF-only occurrence data, which lacks reliable time-of-day fields.

---

# 4. Explicit Boundaries: What This Document Is Not Used For

To keep this knowledge source's role bounded and auditable, Local Ecological Knowledge recorded in this document:

- **Is not used to engineer features.** No feature in the modelling dataset is derived from or weighted by this narrative.
- **Is not used to generate or filter pseudo-absences.** Pseudo-absence design (still Pending per the Dataset Feasibility Study) will be based on documented SDM methodology, not on excluding or favoring locations based on this narrative.
- **Is not used to tune the model.** No hyperparameter, threshold, or model selection decision references this document.
- **Is not used to validate predictions directly.** Model evaluation uses held-out occurrence data and standard metrics (Data & Methodology, Section 12), not agreement with this narrative.
- **Is used only for comparison after modelling is complete** - checking whether independently-derived model outputs happen to align with hypotheses recorded here, which is a legitimate and common practice for triangulating citizen-science/remote-sensing findings against community knowledge in applied ecology.

---

# 5. Status

This document will be revisited once Milestone 3 environmental extraction and later modelling produce outputs to compare against Section 3's hypotheses. New locally-reported knowledge, if it arises during the project, should be appended here with the same attribution discipline (personal vs. community-reported) rather than merged into existing entries.
