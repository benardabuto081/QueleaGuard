# Assumptions & Decision Log

**Project:** QueleaGuard
**Purpose:** Permanent record of significant assumptions made, evidence gathered, and corrections applied during the project lifecycle. Entries are never deleted or rewritten - only appended - so the project's reasoning stays traceable over time.

---

## Log Entry 001 — Nyamware Study Area Correction

**Date:** 2026-07-25 (Phase 2, Milestone 2.1)

**Original assumption:**
The project was scoped around two co-equal irrigation schemes: "Ahero Irrigation Scheme" and "Nyamware Irrigation Scheme," both in Kisumu County, Kenya. This assumption was embedded in the Project Charter, Specification, Technical Architecture, Data & Methodology, Implementation Roadmap, and README Master Specification from project inception.

**Evidence that led to the correction:**
1. During Milestone 2.1 (GBIF occurrence feasibility check), an OpenStreetMap Nominatim search confirmed "Ahero Irrigation Scheme" as a mapped polygon feature, but returned zero results for "Nyamware Irrigation Scheme" under multiple query phrasings.
2. A follow-up Overpass API search for any OSM feature named "Nyamware" within a 20km radius of Ahero returned zero matches across nodes, ways, and relations.
3. A search of authoritative sources - including Kenya's National Irrigation Authority (NIA) official site and multiple independent news reports (2023-2026) covering NIA-led Ahero rehabilitation projects - shows Ahero Irrigation Scheme is a single, gazetted (4,176 acres), NIA-administered scheme established in 1966, composed of named sub-blocks: Ahero, Okana, Mbega, Kasiru/Kolal, Nokiso, Masune, and Kobong'o. "Nyamware" does not appear in any official NIA block listing found.
4. The project owner conducted independent research confirming Nyamware is a village/settlement adjacent to Ahero Irrigation Scheme, part of the surrounding rice-growing community, rather than a separate officially recognized irrigation scheme.

**Corrected understanding:**
There is one irrigation scheme in the study area: **Ahero Irrigation Scheme**. "Nyamware" refers to a village/settlement in the surrounding rice-growing community adjacent to the scheme, not a second irrigation scheme.

**Confidence note:** The evidence gathered directly and strongly supports that Nyamware is *not* an NIA-administered irrigation scheme. It does not, on its own, constitute an authoritative confirmation of Nyamware's precise administrative classification (village vs. sub-location vs. other). This is treated as sufficient evidence to correct project scope, but not as a closed research question - if a more authoritative source (e.g., KNBS, County Government of Kisumu) is encountered later, this entry will be updated accordingly rather than treated as final.

**Rationale for the change:**
Continuing to model "Nyamware Irrigation Scheme" as a second scheme would have embedded a factual error into the project's scientific framing, its disaggregated evaluation design (Specification, Section 12), and its public-facing documentation. Correcting it now, before feature engineering or modelling begins, avoids that error propagating into deliverables that are harder to unwind later (trained models, evaluation reports, README claims).

**Impact of the change:**
- Study area redefined as: **Ahero Irrigation Scheme**, with acknowledgement of surrounding rice-growing communities (including Nyamware village) where relevant to context, framing, or future community-facing use cases.
- "Disaggregated evaluation by irrigation scheme" (Specification, Section 12) is affected - with a single scheme, this becomes disaggregation by sub-block (Ahero, Okana, Mbega, Kasiru/Kolal, Nokiso, Masune, Kobong'o) instead, which is arguably a *stronger* design, since these are real administratively-distinct sub-units rather than an assumed second scheme.
- Project title retained as "QueleaGuard" (not scheme-specific); subtitle/description language updated to reflect single-scheme framing.
- No impact on Milestone 2.1's GBIF findings - those queries used a geographic bounding box, not a scheme-name filter, so the underlying occurrence data remains valid and does not need to be re-pulled.
- All project documents referencing "Nyamware Irrigation Scheme" are being updated to reflect this correction (tracked in Log Entry 002).

**Logged by:** Project owner + AI engineering collaborator, per project collaboration model.

---

## Log Entry 002 — Spatial Framework: Grid-Based Unit of Analysis, Analysis Extent, and Grain Size

**Date:** 2026-07-26 (Phase 2, Milestone 2.4)

**Original assumption:**
The project implicitly assumed the spatial unit of analysis would be either a single polygon representing the whole study area, or polygons representing individual operational blocks within the Ahero Irrigation Scheme (Ahero, Okana, Mbega, Kasiru/Kolal, Nokiso, Masune, Kobong'o, South West Kano, Ayweyo), enabling "disaggregated evaluation by block."

**Evidence that led to the correction:**
1. A search of authoritative sources (National Irrigation Authority, Kenya Open Data, County Government of Kisumu, Ministry of Lands/Survey of Kenya equivalents, and academic/GIS repositories) found no published GIS geometry (shapefile, GeoJSON, KML) for individual NIA operational blocks. NIA publishes block acreage in text form only. Kenya's Open Data portal has a documented history of unreliability. OpenStreetMap contains only a single polygon for the whole scheme (landuse=farmland), with no sub-block subdivision.
2. A review of species distribution modelling (SDM) literature - both general and quelea-specific - found consistent use of regular grid/raster spatial representations rather than administrative or management-unit boundaries. Cheke, Venn & Jones (2007) used quarter-degree grid squares for quelea breeding-suitability forecasting in southern Africa. Dobson et al. (2023, dynamicSDM) used a raster-based SDM approach for Quelea lathamii, with pseudo-absence buffers sized to species movement capability rather than administrative units. No precedent was found for administrative/management-block polygons as a primary SDM spatial unit in quelea-specific, general SDM, or agricultural pest/vector-risk mapping literature reviewed.
3. Grain size (grid cell size) was evaluated against: native resolution of environmental datasets (SRTM 30m, MODIS NDVI 250-500m, CHIRPS ~5.5km/0.05 deg, NASA POWER ~50-55km), occurrence record density (Milestone 2.1: ~110-120 estimated unique space-time events), Red-billed Quelea movement ecology (50-65km daily foraging range, ~30km water-dependency radius, per multiple independent sources), computational efficiency, reproducibility, and consistency with published SDM literature.
4. Buffer distance for the analysis extent was verified empirically: of 161 GBIF/eBird occurrence records pulled in Milestone 2.1, 85.1% fall within 50km of Ahero, versus 77.6% within 30km and 95.7% within 75km - indicating 50km captures a substantial majority of real observations with diminishing marginal return beyond it, independent of the ecological foraging-range argument alone.

**Corrected understanding:**
QueleaGuard adopts a regular spatial grid, not administrative or management-block polygons, as its permanent spatial framework, distinguishing study area from analysis extent from unit of analysis:

- **Study area:** Ahero Irrigation Scheme - the real-world system the project aims to support and the geographic focus of the research.
- **Analysis extent:** Ahero Irrigation Scheme plus a 50km ecologically justified buffer. The buffer distance is grounded in three complementary lines of evidence: (a) ecological literature on Red-billed Quelea daily foraging range (50-65km reported; the conservative lower bound of 50km was selected), (b) empirical verification that 85.1% of confirmed occurrence records fall within this radius of Ahero, and (c) unrestricted availability of environmental predictor data (CHIRPS, MODIS NDVI, SRTM, HydroSHEDS) at this scale, with no coverage gaps. The wider landscape within this radius - including the Nyando River corridor and its connection to Lake Victoria's Winam Gulf - is treated as a plausible ecological landscape influencing quelea movement, consistent with published knowledge of the species' water-dependency and roosting habitat preferences (reed beds/dense vegetation near water). This is not treated as a confirmed or observed roosting area specific to this project; no site-specific roosting survey has been conducted.
- **Spatial unit of analysis:** 5.5km x 5.5km regular grid cells, matching CHIRPS's native resolution. This grain size was selected as a deliberate methodological decision balancing multiple considerations together, not derived from CHIRPS resolution alone: it matches the coarsest scientifically necessary environmental covariate (rainfall) so that no variable is assigned false spatial precision; MODIS NDVI and SRTM-derived variables are aggregated into this grid rather than the reverse; it yields a cell count (roughly 330-360 cells across the full analysis extent) proportionate to current occurrence density rather than producing mostly-empty fine-grained cells; it is consistent with the scale of Red-billed Quelea's landscape-level movement ecology; it is computationally lightweight for the project timeline; and it follows standard multi-resolution SDM literature practice of resampling to the coarsest necessary covariate rather than the finest available one.
- **Prediction target:** infestation risk is predicted for each grid cell within the analysis extent, with the primary decision-support focus remaining the Ahero Irrigation Scheme itself. Grid cells outside the scheme but within the buffer provide modelling context (capturing environmental drivers that influence risk within Ahero) rather than being an end target in their own right.

**Rationale for the change:**
A grid-based framework is supported by two independent justifications, either of which alone would be sufficient: (1) it is the established methodological choice in quelea-specific and general SDM literature, making it more scientifically defensible and more directly citable in an eventual publication than an administrative-unit approach; and (2) authoritative boundaries for individual operational blocks do not exist in any accessible open source, making a block-based model difficult to reproduce and impossible to verify independently. The grid-based approach also resolves the disaggregated-evaluation question left open in Log Entry 001 - rather than evaluating by named block (which would require boundaries we don't have), disaggregated evaluation can now be performed by spatial cross-validation fold or by distance-from-scheme-center, which is both more standard SDM practice and does not depend on any unverified boundary data.

**Impact of the change:**
- Specification, Technical Architecture, Data & Methodology, Dataset Feasibility Study, and Implementation Roadmap all require updates to reflect study area / analysis extent / unit of analysis as three distinct, explicitly defined concepts, replacing prior single "study area" framing.
- The "disaggregated evaluation by irrigation scheme sub-block" language introduced in Log Entry 001 is superseded by disaggregated evaluation by spatial partition (e.g., CV fold or distance band) within the grid framework.
- No re-collection of existing data is required. Milestone 2.1's GBIF pull and Milestone 2.3's CHIRPS pilot both remain valid and reusable under this framework.
- This spatial framework is treated as a fixed project standard going forward and should be referenced consistently in all future documentation and in the eventual manuscript's Methods/Study Area section.

**Logged by:** Project owner + AI engineering collaborator, per project collaboration model.

---

## Log Entry 003 — Meteorology Source: ERA5-Land Selected Over NASA POWER

**Date:** 2026-08-01 (Phase 2, Milestone 2.5)

**Original assumption:**
Meteorology source (temperature, humidity, wind) was left "Under Review" between NASA POWER and ERA5-Land in the Dataset Feasibility Study, Section 7.

**Evidence that led to the decision:**
1. Both sources were piloted directly. NASA POWER: instant, no-authentication REST API access confirmed, real values retrieved for Ahero (Jan 2024). ERA5-Land: access confirmed via Copernicus CDS API following one-time account registration and dataset license acceptance; request processed and NetCDF file downloaded successfully in under 30 seconds.
2. Resolution comparison: NASA POWER (~50-55km, per its own documentation) vs. ERA5-Land (~9km, per its own documentation), against the project's adopted 5.5km analysis grid (Log Entry 002).
3. At NASA POWER's resolution, the project's full ~100km-wide analysis extent (Ahero + 50km buffer) would be covered by only 2-4 distinct meteorology values total, meaning the large majority of the project's ~330-360 grid cells would receive near-identical temperature/humidity/wind readings, contributing temporal but not spatial signal - a limitation already flagged as a risk in the original Dataset Feasibility Study (Section 2.2). ERA5-Land's ~9km resolution allows meaningfully distinct values between neighboring grid cells.

**Corrected/finalized understanding:**
**ERA5-Land is selected as the project's meteorology source** (temperature, dewpoint/humidity, wind), superseding NASA POWER. Access is via the Copernicus CDS API (`cdsapi` Python package), requiring one-time free registration and dataset license acceptance - both completed.

**Rationale for the decision:**
Spatial resolution is the deciding factor over convenience. NASA POWER's no-authentication access is a real convenience but does not offset a resolution gap severe enough to make the variable spatially uninformative across most of the analysis extent. ERA5-Land's one-time registration cost is trivial relative to the improvement in spatial signal quality.

**Impact of the decision:**
- Dataset Feasibility Study, Section 7 ("Engineering Decisions") and Section 9 ("Dataset Status Tracker") updated: ERA5-Land marked Approved/Selected, NASA POWER marked Not Selected (retained as a documented, evaluated alternative, not deleted from the record).
- `src/nasa_power_pilot.py` and `src/era5land_pilot.py`, along with their reference outputs in `reports/`, are retained as evidence of the comparison, consistent with the project's publication-readiness standard (both a positive and a superseded result are preserved, not just the final choice).
- No other documents require correction, as none had committed to NASA POWER specifically prior to this decision (all referenced it as "NASA POWER or ERA5-Land").

**Logged by:** Project owner + AI engineering collaborator, per project collaboration model.

---

## Log Entry 004 — Occurrence-to-Grid Join: Persistent Site Identified in Buffer Zone

**Date:** 2026-08-01 (Phase 3, Milestone 3.2)

**Context:**
During the occurrence-to-grid spatial join (Milestone 3.2), 145 of 161 raw GBIF/eBird records (Milestone 2.1) matched to a grid cell within the analysis extent; 16 fell outside it. Of matched records, one grid cell (cell_0080) accounted for 62 records (43% of matched records) - a concentration warranting investigation before being treated as clean data.

**Finding:**
Investigation confirmed this concentration reflects genuine repeated observation of a persistent site, not a duplication artifact: the 62 records span 36 distinct dates across a 1984-2024 date range, from many different individual observers (no observer contributing more than 2 records), clustered within approximately 100 meters of each other. The site sits within the analysis extent's ecological buffer (not within the Ahero scheme boundary itself), approximately 20.6km west of Ahero and geographically consistent with the shoreline of Lake Victoria's Winam Gulf near Kisumu.

**Interpretation (deliberately bounded):**
This finding is consistent with - but does not confirm - the "plausible ecological landscape" reasoning in Log Entry 002 regarding the Nyando River/Lake Victoria corridor's potential influence on quelea movement in the study area. It is evidence of a persistent, repeatedly-visited site near water, within the buffer zone the project defined for ecological reasons. It is not evidence of a confirmed roosting or breeding site - no site-specific ecological survey has been conducted, and citizen-science observation frequency reflects observer accessibility and interest as well as bird presence. This distinction is maintained consistently with the wording standard set in Log Entry 002.

**Relevance to the project:**
This is a concrete, data-derived example of why the 50km ecological buffer (rather than the scheme boundary alone) was methodologically appropriate: a real, repeatedly-documented site of interest exists within the buffer and would have been excluded entirely under a scheme-only study area. This strengthens (with real evidence, not just literature-based projection) the justification recorded in Log Entry 002.

**No methodology change results from this entry** - it is a documentation of a finding that validates an existing decision, not a correction to it.

**Logged by:** Project owner + AI engineering collaborator, per project collaboration model.

---

## Log Entry 005 — Local Ecological Knowledge Recorded as Separate Artifact

**Date:** 2026-08-01 (Phase 3, Milestone 3.2)

**Context:**
The project owner disclosed local ecological knowledge relevant to quelea behavior near the Ahero Irrigation Scheme, distinguishing personal observations (from growing up near the scheme) from secondhand community-reported knowledge (accounts from local farmers and residents regarding shoreline roosting and dawn feeding-ground movement, and floodplain/high-lake-level flooding history).

**Decision:**
This knowledge is recorded in a dedicated document, docs/local_ecological_knowledge_and_hypotheses.md, kept explicitly separate from project methodology. It is not treated as evidence, not incorporated into feature engineering, pseudo-absence generation, model tuning, or validation. Its sole role is generating testable hypotheses (five recorded, H1-H5) to be checked against model outputs and data patterns after modelling is complete, not before.

**Rationale:**
Local ecological knowledge is a recognized, legitimate input in applied ecological research, but conflating it with empirical evidence risks quietly biasing methodology toward a pre-existing narrative. Keeping it as a separate, clearly-attributed, clearly-bounded artifact preserves its value (hypothesis generation, eventual triangulation with model results) while protecting the scientific integrity of the modelling pipeline itself. This is consistent with the project's Responsible AI principles (transparency about knowledge sources) and its publication-readiness goal (LEK sections are a recognized, citable practice in applied ecology papers).

**Specific care taken on attribution and place-naming:**
Personal observation and community-reported knowledge are distinguished explicitly in the document, rather than presented uniformly as "local knowledge." The claim that Nyamware specifically is one of the areas most affected by quelea is recorded strictly as a locally-held belief, not as fact, and is explicitly flagged as unverifiable at present given Nyamware's location and extent remain unresolved (Log Entry 001).

**Relationship to Log Entry 004:**
The persistent occurrence site identified empirically in Log Entry 004 (cell_0080, near the Winam Gulf shoreline) is noted in the LEK document as broadly consistent with the community-reported shoreline-roosting narrative. This is stated as two independent sources pointing in a similar direction, not as confirmation of either one by the other.

**Impact:**
No change to methodology, spatial framework, feature engineering plan, or any prior decision. This entry documents the existence and intended treatment of a new qualitative knowledge source only.

**Logged by:** Project owner + AI engineering collaborator, per project collaboration model.

---

## Log Entry 006 — Temporal Feature Engineering Framework

**Date:** 2026-08-01 (Phase 3, Milestone 3.3)

**Context:**
Following the spatial framework (Log Entry 002), a corresponding temporal methodology was needed before environmental feature extraction could begin, since the project's goal is to predict occurrence based on conditions plausibly influencing birds before observation, not long-run average conditions at a location.

**Decision:**
QueleaGuard adopts per-occurrence, date-matched environmental features (not static per-cell climatology), with variable-specific temporal representations chosen for ecological reasons:

- **Rainfall (CHIRPS):** multi-window antecedent accumulation (7-day, 30-day, 90-day totals preceding the observation date). Rationale: rainfall's ecological effect on quelea is lagged and cumulative - rain drives seed/grass growth over a period of weeks, which in turn drives food availability and breeding (Cheke, Venn & Jones 2007) - not an instantaneous same-day effect. Multiple windows allow the eventual model to reveal which lag is most predictive rather than assuming one in advance.
- **Vegetation (MODIS NDVI):** nearest 16-day composite value at or before the observation date, plus an NDVI anomaly feature (deviation from that cell's typical seasonal NDVI). Rationale: NDVI is itself already a state variable representing current vegetation greenness, not a quantity that should be further accumulated over time; anomaly captures ecologically meaningful deviation from local seasonal norms, consistent with vegetation-flush-driven breeding cues in the literature.
- **Meteorology (ERA5-Land - temperature, humidity, wind):** short window (7-day mean) plus same-day/nearest-day value. Rationale: these variables plausibly act more immediately on bird activity and flight/foraging conditions than on a lagged biological process, so a short window is mechanistically appropriate rather than an arbitrary simplification.
- **Terrain/hydrology (SRTM elevation/slope, HydroSHEDS distance-to-water):** static, no temporal dimension. Rationale: these are physically time-invariant at any timescale relevant to this project.

**Raw dataset vs. modelling dataset distinction (explicit):**
The raw occurrence dataset (161 records, Milestone 2.1) and grid-matched dataset (145 records, Milestone 3.2) are retained in full and continue to be used in exploratory analyses, temporal summaries, and project documentation regardless of this decision. The temporal framework above defines a separate, feature-complete **modelling dataset**, which additionally requires every environmental variable to be extractable for a given record's date.

**MODIS NDVI as the effective temporal boundary:**
Since MODIS NDVI (operational from February 2000) is a core planned feature - not optional - and CHIRPS (1981-present) and ERA5-Land (confirmed via direct verification to cover 1950-present) both cover the full occurrence record range, MODIS's start date is the binding constraint on the modelling dataset's usable temporal range. This mirrors the spatial framework's logic (Log Entry 002), where CHIRPS's resolution was identified as the coarsest necessary layer and other sources were matched to it; here, MODIS's start date plays the equivalent temporal role.

**Quantified impact (Milestone 3.3):**
Of 145 occurrence records matched to the analysis grid (Milestone 3.2):
- 133 records (91.7%) fall on or after January 2000 and are feature-complete modelling dataset candidates.
- 8 records (5.5%) predate 2000 and are excluded from the feature-complete modelling dataset. These remain valid historical occurrence evidence and are retained in the raw and grid-matched datasets for EDA, temporal summaries, and documentation - the exclusion reflects a data availability constraint, not a data quality judgement about these specific observations.
- 4 records (2.8%) have missing or unparseable year values and require separate handling (to be resolved during Milestone 3 preprocessing, not this decision).

One excluded pre-2000 record (1984-12-29) shares coordinates with cell_0080, the persistent site identified in Log Entry 004 - additional, non-decisive context suggesting that site's observation pattern may extend back further than the feature-complete dataset can capture.

**Dependency acknowledged, not yet resolved:**
Pseudo-absence generation (Dataset Feasibility Study, Section 7 - status Pending) will require each generated pseudo-absence point to carry an associated date, so that environmental variables can be extracted for pseudo-absences using the same variable-specific temporal logic defined here. This is a formal requirement on the eventual pseudo-absence methodology, not a detail to be decided implicitly when that design work happens.

**Rationale for the framework overall:**
Matching temporal representation to each variable's actual ecological mechanism, rather than applying one uniform convention (e.g., "always use monthly averages"), is more scientifically defensible and more consistent with published SDM practice, and produces a methodology that can be justified point-by-point in an eventual publication's Methods section rather than asserted without support.

**Logged by:** Project owner + AI engineering collaborator, per project collaboration model.

---
