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

## Log Entry 007 — CHIRPS Direct-Read Access Pattern and Rainfall Feature Extraction

**Date:** 2026-08-01 (Phase 3, Milestone 3.4)

**Context:**
Initial rainfall extraction attempts used a live remote API (NOAA ERDDAP CHIRPS mirror), which proved unreachable (connection timeouts), and subsequently a per-record download-and-decompress approach, which was inefficient (repeated temporary file creation) and triggered a geographic-CRS centroid computation warning.

**Technical finding - direct compressed raster reading:**
GDAL (and therefore rasterio, which is built on GDAL) supports reading gzip-compressed raster files directly via its `/vsigzip/` virtual filesystem, without decompressing to disk. This was confirmed empirically: rasterio's higher-level `gz://` and `gz+file://` URI schemes did not resolve correctly on this Windows/rasterio installation (confirmed via smoke test, both failed with "not recognized as a supported dataset name"), but the underlying raw GDAL path syntax (`/vsigzip/<absolute_posix_path>`) worked correctly and returned results identical to a fully decompressed read (25.94mm rainfall at Ahero, 2024-01-15, matching the Milestone 2.3 pilot exactly).

**Extraction architecture adopted:**
1. Grid cell centroids computed via a projected metric CRS (EPSG:32736, UTM Zone 36S - consistent with grid generation, Log Entry 002/Milestone 3.1), then reprojected to WGS84, avoiding the geographic-CRS centroid inaccuracy warning correctly rather than suppressing it.
2. A local cache of all 3,247 unique CHIRPS daily raster files needed to cover every record's 90-day antecedent window (per Log Entry 006) was downloaded once via src/download_chirps_cache.py (10.84GB, resumable, courtesy-delayed).
3. Extraction is batched by date, not by record: each unique daily raster is opened exactly once via `/vsigzip/`, all grid cells needing a value on that date are extracted in a single pass, then the file is closed. This guarantees each of the 3,247 files is opened at most once regardless of how many records/cells reference it (5,965 total (date, cell) extractions required across only 3,247 file opens).

**Outcome:**
All 133 modelling-candidate records successfully extracted with complete 91-day coverage (0 missing files, 0 incomplete records). Total extraction time: ~17.5 minutes. Rainfall features (7-day, 30-day, 90-day antecedent totals) saved to data/processed/rainfall_features.csv.

**Rationale for recording this as a Decision Log entry rather than only in code comments:**
The `/vsigzip/` finding and the URI scheme failure on this system are non-obvious and would otherwise need to be rediscovered by anyone reproducing this pipeline (a stated project priority - see docs/assumptions_and_decision_log.md project-wide reproducibility principle, and the Scientific Publication & Research Strategy). Documenting it here, alongside the architectural decision to batch by date rather than by record, preserves both the technical solution and the reasoning for future reuse (this pattern will be reused for ERA5-Land and MODIS NDVI extraction).

**Impact:**
No change to prior decisions (spatial framework, temporal framework, or data sources). This entry documents implementation methodology for Milestone 3.4, establishing a reusable extraction pattern for subsequent environmental variables.

**Logged by:** Project owner + AI engineering collaborator, per project collaboration model.

---

## Log Entry 008 — ERA5-Land Batched Extraction and CDS ZIP Format Finding

**Date:** 2026-08-02 (Phase 3, Milestone 3.5)

**Context:**
Following the CHIRPS extraction pattern (Log Entry 007), ERA5-Land meteorology features (temperature, dewpoint/humidity, wind - 7-day mean + same-day, per Log Entry 006) were extracted for all 133 modelling-candidate records via the Copernicus CDS API.

**Efficient batching approach:**
Rather than one CDS request per record (133 requests) or per unique date (480 unique dates across all 7-day windows), requests were batched by (year, month) - only 60 unique combinations needed, since the CDS API supports requesting multiple specific days within a single month in one call. All 60 requests completed successfully (one transient connection error was automatically retried by the cdsapi client's built-in retry logic, with no data loss).

**Technical finding - CDS returns ZIP archives despite requesting NetCDF format:**
Downloaded files, despite the request specifying `"data_format": "netcdf"`, were ZIP archives (confirmed via file signature inspection: `PK\x03\x04`) containing the actual `.nc` file inside, not raw NetCDF files. This is a known current behavior of some CDS datasets and is not documented prominently on the API usage page. The extraction script now detects this via file signature (not file extension, which is unreliable) and extracts automatically before reading with xarray.

**Outcome:**
All 133 records successfully extracted with complete 7/7-day coverage (0 incomplete records). Meteorology features (temp_mean_7d, dewpoint_mean_7d, wind_mean_7d, and same-day equivalents) saved to data/processed/meteorology_features.csv.

**Rationale for recording this as a Decision Log entry:**
Like the CHIRPS /vsigzip/ finding (Log Entry 007), this is a non-obvious technical detail that would otherwise need rediscovery by anyone reproducing this pipeline. The (year, month) batching strategy is also a reusable pattern worth documenting explicitly for the MODIS NDVI extraction still to come.

**Impact:**
No change to prior decisions. Documents implementation methodology for Milestone 3.5.

**Logged by:** Project owner + AI engineering collaborator, per project collaboration model.

---

## Log Entry 009 — Pseudo-Absence Generation Methodology: Approximate Target-Group Background Sampling

**Date:** 2026-08-03 (Phase 3, Milestone 3.9)

**Context:**
Pseudo-absence generation strategy had remained "Pending" in the Dataset Feasibility Study (Section 7) since Milestone 2. Before any implementation, a structured literature review was conducted comparing candidate strategies against this project's specific characteristics: 133 modelling-candidate presence records, a documented GBIF/eBird observer-effort bias (Milestone 2.1: 78% of records from eBird; Log Entry 004: 43% of matched records concentrated in a single grid cell, cell_0080), the established grid-based spatial framework (Log Entry 002), and the temporal framework requiring every pseudo-absence to carry an assigned date (Log Entry 006).

**Candidate strategies evaluated:**

| Strategy | Strengths | Limitations for this project | Selected? |
|---|---|---|---|
| Random background sampling (Barbet-Massin et al. 2012) | Simple, most widely used in the literature (~92% of surveyed presence-only SDM studies use some random component); well-documented guidance on presence:background ratio by model type | Assumes roughly even sampling effort across the study area - an assumption directly contradicted by our own data (cell_0080 concentration; eBird hotspot bias). Would risk teaching the model "far from birding hotspots" as ecological absence rather than unobserved presence | No |
| Environmentally stratified / profile-based sampling (e.g., BIOCLIM-envelope two-step methods; Engler et al. 2004) | Can produce more geographically constrained predictions | Documented to produce overly optimistic, narrow predictions and risks circular reasoning (defining absence by environmental dissimilarity, then "discovering" environment predicts presence) (Engler et al. 2004; Lobo et al. 2010) | No |
| Target-Group Background, full checklist-based (Phillips et al. 2009; validated for bird citizen-science data with known ground-truth effort by Barber et al. 2022, Diversity and Distributions) | Directly corrects observer-effort bias rather than ignoring it; specifically validated on bird citizen-science platforms; naturally provides a real, defensible date per pseudo-absence (a checklist's date), directly satisfying the Log Entry 006 dependency | Requires complete checklist data (including explicit non-detections), which requires eBird's full EBD dataset - access not yet secured (Dataset Feasibility Study, Section 2.1: eBird EBD requires a data-use request, approval not instant) | Not yet (see "approximate" version below) |
| Target-Group Background, approximate (this project's adopted approach) | Implementable now using existing GBIF API access; still directly targets the documented observer-effort bias by using other species' occurrence records as a proxy for "birding effort occurred here" | Weaker than full-checklist TGB: individual species occurrence records are a noisier proxy for effort than complete checklists, since they don't capture explicit non-detection events at the same reliability | **Yes (primary method)** |
| Spatial thinning of presences (STSP) | Reduces spatial autocorrelation from clustered records (directly relevant to cell_0080/cell_0156 concentration) | Does not, on its own, correct observer-effort bias - a complementary technique, not a substitute for TGB | Yes (combined with TGB, not standalone) |
| Advanced observer-weighted methods (e.g., presence-weighted observer-oriented approach, kernel density of per-observer effort) | More sophisticated bias correction, captures individual observer behaviour patterns | Requires rich per-observer effort data across many species/records to estimate reliably; overpowered and likely underdetermined given only 133 presence records | No |

**Decision:**
QueleaGuard adopts **approximate Target-Group Background (TGB) sampling** as its pseudo-absence generation strategy, combined with light spatial thinning to avoid over-concentration at known hotspots (cell_0080, cell_0156). Pseudo-absences will be drawn from locations and dates where other bird species were recorded via GBIF within the analysis extent (Log Entry 002), but *Quelea quelea* was not the species logged at that location/date. This is explicitly an **approximation of true checklist-based TGB**, not the full method described in Phillips et al. (2009) and validated by Barber et al. (2022) - the distinction is being stated explicitly here and must be carried through all subsequent documentation (README, Data & Methodology, and any eventual manuscript) rather than presented as equivalent to full-checklist TGB.

**Explicit limitation statement:**
This approximation is weaker than full-checklist TGB because individual GBIF occurrence records for other species do not reliably capture explicit non-detection ("surveyed, not seen") events the way complete eBird checklists do - a location with no *other*-species record either could genuinely be unvisited, or could reflect incomplete GBIF republishing of an eBird checklist. This limitation will be stated plainly in the Data & Methodology document and the eventual Responsible AI / Limitations sections, not minimized. Pursuing eBird EBD access remains a documented, credible path to upgrading this to full-checklist TGB in future work, per the Dataset Feasibility Study's original recommendation (Section 5).

**Presence:pseudo-absence ratio:**
A moderate, near-balanced ratio will be used (informed by Barbet-Massin et al. 2012's finding that tree-based machine learning methods - Random Forest, Gradient Boosting, both planned per the Technical Architecture - perform best with ratios closer to 1:1, unlike regression-based SDMs which tolerate much larger imbalanced background samples). The exact ratio will be finalized during implementation and reported transparently.

**Key citations:**
- Barbet-Massin, M., Jiguet, F., Albert, C.H., Thuiller, W. (2012). Selecting pseudo-absences for species distribution models: how, where and how many? *Methods in Ecology and Evolution*, 3, 327-338.
- Phillips, S.J. et al. (2009). Sample selection bias and presence-only distribution models: implications for background and pseudo-absence data. *Ecological Applications*, 19(1), 181-197. [Target-Group Background method]
- Barber, R.A. et al. (2022). Target-group backgrounds prove effective at correcting sampling bias in Maxent models. *Diversity and Distributions*, 28, 128-141. [Bird citizen-science validation with known ground-truth effort]
- Engler, R., Guisan, A., Rechsteiner, L. (2004). An improved approach for predicting the distribution of rare and endangered species from occurrence and pseudo-absence data. *Journal of Applied Ecology*, 41(2), 263-274. [Limitation of profile-based methods]

**Rationale for the decision:**
Approximate TGB is the only evaluated strategy that directly addresses the specific, empirically-documented observer-effort bias in this project's data while remaining implementable with currently-available access (GBIF API, no pending EBD approval dependency), and it uniquely resolves the pseudo-absence dating requirement (Log Entry 006) as a natural byproduct of the method rather than a separate problem to solve. Choosing it over full-checklist TGB is a documented, honest scope decision - not a claim of methodological equivalence.

**Impact:**
Dataset Feasibility Study, Section 7 ("Pseudo-absence generation strategy") updated from Pending to Approved (approximate TGB). Implementation proceeds next: querying GBIF for other-species records within the analysis extent, spatial thinning, and construction of the final presence/pseudo-absence modelling dataset.

**Logged by:** Project owner + AI engineering collaborator, per project collaboration model.

---

## Log Entry 010 — Pseudo-Absence Scheme-Boundary Coverage Gap: Evaluated and Resolved (Option 1 Confirmed)

**Date:** 2026-08-03 (Phase 3, Milestone 3.9)

**Context:**
During implementation of approximate Target-Group Background pseudo-absence sampling (Log Entry 009), the final sampled pseudo-absence set (133 records, 1:1 ratio with presences) contained zero records within the 4 grid cells comprising the Ahero scheme boundary (of 328 total grid cells). Investigation confirmed this was not a pipeline defect: the underlying effort-proxy pool (2,400 other-species GBIF records, evenly sampled across the 16 years spanning the presence dataset) contains zero records within the scheme boundary at any stage, before or after thinning. Scheme-boundary presence records do exist (Milestone 3.2: 30 of 133 presence records fall within scheme-boundary cells).

**Options evaluated (full comparison in conversation record):**
1. Continue with approximate TGB project-wide; document the scheme-boundary gap as a limitation.
2. Introduce a narrowly-scoped hybrid strategy for the 4 scheme cells only.
3. Replace the pseudo-absence methodology entirely.

Each option was assessed against five criteria: scientific validity, bias-introduction risk, literature support, reproducibility impact, and effect on project credibility. Option 2 was rejected because it would reintroduce the exact observer-effort bias TGB was adopted to correct (Log Entry 009), specifically within the zone most relevant to decision-support - the worst location to relax the correction. Option 3 was rejected as disproportionate: the affected area is 4 of 328 cells (~1.2% of the grid), and abandoning a literature-grounded, empirically-motivated methodology because of a small localized gap would be a reactive rather than evidence-driven decision.

**Empirical verification performed before finalizing:**
Before accepting Option 1, the assumption that the model could reasonably interpolate (rather than extrapolate) predictions for the 4 scheme cells was checked empirically, not assumed. The 4 scheme cells' elevation, slope, and distance-to-water values (Milestone 3.7, 3.8) were compared against the full 328-cell grid's distribution:
- Elevation: scheme cells at the 15th-17th percentile of the full grid range - low-lying but well within the range shared by 324 other cells (25th percentile of the full grid is closely comparable).
- Slope: scheme cells at the 10th-18th percentile - similarly common, not an extreme or isolated value.
- Distance to water: scheme cells span the 5th-54th percentile - well distributed within the observed range (grid max: 4,163m; scheme cells: 81-1,022m).

This supports the conclusion that the scheme cells occupy a well-represented portion of the environmental covariate space (terrain and hydrology specifically) rather than an isolated or extreme niche, making model interpolation for these cells a reasonable, evidence-supported expectation rather than an unverified assumption.

**Decision (confirmed):**
**Option 1 is adopted.** Approximate Target-Group Background sampling (Log Entry 009) proceeds as the project's pseudo-absence methodology, applied uniformly across the full analysis extent, with the following limitation stated explicitly in project documentation (README, Data & Methodology, and any eventual manuscript):

> *The pseudo-absence sampling pool contains no candidate records within the 4 grid cells (of 328) comprising the Ahero scheme boundary itself, because no other-species effort-proxy records were found there across a 16-year, 2,400-record sample. Model predictions for these cells rely on interpolation from environmentally similar cells elsewhere in the analysis extent (empirically verified as reasonable for elevation, slope, and distance-to-water), rather than from locally-sampled presence/absence contrast. This is a bounded, documented limitation affecting approximately 1.2% of the analysis grid, not a defect in the overall methodology.*

**Scope note on NDVI:**
A related but analytically distinct question was raised during this validation - whether NDVI feature coverage has a similar or different gap for scheme-boundary cells - but was explicitly not verified with sufficient rigor to document as a limitation here. This remains an open item pending direct verification against the actual modelling pipeline's NDVI feature construction (not just AppEEARS task membership), to avoid overstating the evidence. To be resolved as its own follow-up before final dataset assembly.

**Rationale:**
This entry demonstrates the project's evidence-first decision process functioning as intended: an unexpected result (zero scheme-boundary pseudo-absences) was investigated rather than assumed to be either a bug or a methodology failure, alternatives were compared systematically against explicit criteria, and the leading option was verified empirically before being finalized rather than accepted on reasoning alone.

**Impact:**
Pseudo-absence dataset (data/processed/pseudo_absences_final.csv, 133 records) is confirmed as final, pending the separate NDVI verification noted above. Dataset Feasibility Study Section 7 pseudo-absence status remains Approved (as set in Log Entry 009), now with this documented limitation attached.

**Logged by:** Project owner + AI engineering collaborator, per project collaboration model.

---

## Log Entry 011 — Pseudo-Absence Month-Only Date Precision Handling

**Date:** 2026-08-04 (Phase 3, Milestone 3.10)

**Context:** 2 of 133 pseudo-absence records (keys 3030837070, 3030479318, both grid_cell_id cell_0301) had month-only precision dates (2020-01) rather than full day-level dates, consistent with the known GBIF data quality characteristic documented in Milestone 2.1 (some records only report year/month).

**Decision:** Both records assigned day-01 of the given month as a defensible placeholder, enabling daily environmental feature extraction. This is a minor, disclosed precision reduction affecting 2 of 266 total modelling records (0.75%), not a methodology change.

**Impact:** No other records affected. Documented here for traceability per project reproducibility standards.

**Logged by:** Project owner + AI engineering collaborator, per project collaboration model.

---

## Log Entry 012 — Post-NDVI-Fix Pseudo-Absence Exclusion: MODIS Temporal Boundary (4 Records)

**Date:** 2026-08-12 (Phase 3, Milestone 3.10)

**Context:** Task 190 fixed a bug in NDVI extraction where the MODIS fill value (-3000, "Pixel not produced due to other reasons than clouds") was being selected as a valid nearest-composite value in 8 of 266 records, because the good-quality filter was applied only to the seasonal baseline calculation, not to nearest-composite selection itself. The fix (filtering to good-quality composites before any selection logic runs) resolved all 8 out-of-range values (5 presence, 3 pseudo-absence). However, applying the corrected logic surfaced a new, distinct finding: 4 pseudo-absence records (keys 46827633, 46827634 at cell_0283; 1772792042, 1772792055 at cell_0146), all dated mid-to-late January 2000, had no valid prior good-quality composite at all. Diagnosis confirmed both cells have healthy overall NDVI coverage (560 and 545 good-quality composites respectively) but their earliest good-quality composite is 2000-02-18 — these 4 records simply predate MODIS's first valid data by roughly 3-6 weeks. This is the same root cause as the 8 pre-2000 presence records already excluded in Log Entry 006 (MODIS Terra's operational start, not a data quality defect), surfacing here because the existing presence-side `year >= 2000` filter is an approximate proxy that doesn't precisely exclude early-2000 dates before the 2000-02-18 boundary, and no equivalent filter had been applied to pseudo-absence records.

**Decision:** Exclude these 4 records from the modelling dataset. Not backfilled with replacement pseudo-absences. `assemble_final_dataset.py` was generalized to add a post-merge completeness filter that drops any record (presence or pseudo-absence) missing a valid NDVI value, rather than relying solely on the approximate year-based proxy — this makes the exclusion rule from Log Entry 006 apply uniformly and automatically to both classes going forward, including in any future re-run of the pipeline.

**Impact:** Final modelling dataset size changes from 266 to **262 records**. Class balance changes from the originally planned exact 1:1 (133:133, Log Entry 009) to **133 presence : 129 pseudo-absence**. This is a minor departure from exact balance (67.5%/49.2% split by class, effectively ~50.8%/49.2%) and does not warrant class-weighting or resampling — the imbalance is negligible for the tree-based models planned (Random Forest, Gradient Boosting) per Barbet-Massin et al. 2012's guidance already cited in Log Entry 009. No backfill was performed, consistent with the precedent set in Log Entry 006 (the original 8 pre-2000 presence exclusions were also not backfilled; the project accepted N=133 rather than re-sampling to restore a round number). This exclusion is a data availability constraint, not a data quality judgement, and must be described that way in any future documentation (Responsible AI statement, paper Methods section, Data Dictionary).

**Logged by:** Project owner + AI engineering collaborator, per project collaboration model.

---

## Log Entry 013 — Pseudo-Absence / Presence Checklist Contradiction: TGB Assumption Violation (3 Records)

**Date:** 2026-08-12 (Phase 3, Milestone 3.11)

**Context:** Milestone 3.11 validation added a cross-class check (grid_cell_id + observation_date pairs appearing in both presence and pseudo-absence records), which had never been run in any prior validation pass. It found exactly one conflicting pair: cell_0079, 2016-01-17, containing 1 confirmed *Quelea quelea* presence record (key 1710848647) and 3 pseudo-absence records (keys 1710847627, 1710847782, 1710848645) drawn from the all-species effort-proxy pool. All four keys are sequential, strongly indicating they originate from a single shared eBird checklist. This is a genuine violation of the Target-Group Background pseudo-absence assumption established in Log Entry 009: a TGB pseudo-absence represents "an observer was present at this location/time and did not detect the target species." That assumption cannot hold for a checklist that demonstrably did detect *Quelea quelea* — the 3 other-species records from that same checklist were incorrectly eligible as absence proxies. This is a gap in the original pseudo-absence pool construction (Log Entry 009), not a new methodology question: standard TGB practice requires excluding effort-proxy records that co-occur with a confirmed target-species detection at the same checklist/location/date, and this exclusion step was missing.

**Decision:** Exclude the 3 contradicting pseudo-absence records from the modelling dataset. Not backfilled, consistent with the precedent in Log Entry 006 and Log Entry 012. `assemble_final_dataset.py`'s output was corrected directly rather than treating this as a scope-level decision requiring sign-off, since the resolution follows unambiguous, standard TGB practice rather than involving a genuine choice between alternatives.

**Impact:** Final modelling dataset size changes from 262 to **259 records**. Class balance changes from 133:129 to **133 presence : 126 pseudo-absence**. Cumulative effect of Log Entry 012 + 013: the originally planned exact 1:1 balance (266 records, Log Entry 009) is now 133:126 (259 records total, ~51.4%/48.6% split) — still close enough to balanced that no class-weighting or resampling is needed for the planned tree-based models. This finding should also inform a durable safeguard: if the pseudo-absence pool is ever regenerated (`build_pseudo_absence_pool.py`, `sample_pseudo_absences.py`), a checklist/date/cell exclusion filter against known presence records should be added at that stage, not discovered again post-hoc during validation.

**Logged by:** Project owner + AI engineering collaborator, per project collaboration model.

---
