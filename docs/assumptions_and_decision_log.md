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

**Logged by:** Project owner

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

**Logged by:** Project owner

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

**Logged by:** Project owner

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

**Logged by:** Project owner

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

**Logged by:** Project owner

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

**Logged by:** Project owner

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

**Logged by:** Project owner

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

**Logged by:** Project owner

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

**Logged by:** Project owner

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

**Logged by:** Project owner

---

## Log Entry 011 — Pseudo-Absence Month-Only Date Precision Handling

**Date:** 2026-08-04 (Phase 3, Milestone 3.10)

**Context:** 2 of 133 pseudo-absence records (keys 3030837070, 3030479318, both grid_cell_id cell_0301) had month-only precision dates (2020-01) rather than full day-level dates, consistent with the known GBIF data quality characteristic documented in Milestone 2.1 (some records only report year/month).

**Decision:** Both records assigned day-01 of the given month as a defensible placeholder, enabling daily environmental feature extraction. This is a minor, disclosed precision reduction affecting 2 of 266 total modelling records (0.75%), not a methodology change.

**Impact:** No other records affected. Documented here for traceability per project reproducibility standards.

**Logged by:** Project owner

---

## Log Entry 012 — Post-NDVI-Fix Pseudo-Absence Exclusion: MODIS Temporal Boundary (4 Records)

**Date:** 2026-08-12 (Phase 3, Milestone 3.10)

**Context:** Task 190 fixed a bug in NDVI extraction where the MODIS fill value (-3000, "Pixel not produced due to other reasons than clouds") was being selected as a valid nearest-composite value in 8 of 266 records, because the good-quality filter was applied only to the seasonal baseline calculation, not to nearest-composite selection itself. The fix (filtering to good-quality composites before any selection logic runs) resolved all 8 out-of-range values (5 presence, 3 pseudo-absence). However, applying the corrected logic surfaced a new, distinct finding: 4 pseudo-absence records (keys 46827633, 46827634 at cell_0283; 1772792042, 1772792055 at cell_0146), all dated mid-to-late January 2000, had no valid prior good-quality composite at all. Diagnosis confirmed both cells have healthy overall NDVI coverage (560 and 545 good-quality composites respectively) but their earliest good-quality composite is 2000-02-18 — these 4 records simply predate MODIS's first valid data by roughly 3-6 weeks. This is the same root cause as the 8 pre-2000 presence records already excluded in Log Entry 006 (MODIS Terra's operational start, not a data quality defect), surfacing here because the existing presence-side `year >= 2000` filter is an approximate proxy that doesn't precisely exclude early-2000 dates before the 2000-02-18 boundary, and no equivalent filter had been applied to pseudo-absence records.

**Decision:** Exclude these 4 records from the modelling dataset. Not backfilled with replacement pseudo-absences. `assemble_final_dataset.py` was generalized to add a post-merge completeness filter that drops any record (presence or pseudo-absence) missing a valid NDVI value, rather than relying solely on the approximate year-based proxy — this makes the exclusion rule from Log Entry 006 apply uniformly and automatically to both classes going forward, including in any future re-run of the pipeline.

**Impact:** Final modelling dataset size changes from 266 to **262 records**. Class balance changes from the originally planned exact 1:1 (133:133, Log Entry 009) to **133 presence : 129 pseudo-absence**. This is a minor departure from exact balance (67.5%/49.2% split by class, effectively ~50.8%/49.2%) and does not warrant class-weighting or resampling — the imbalance is negligible for the tree-based models planned (Random Forest, Gradient Boosting) per Barbet-Massin et al. 2012's guidance already cited in Log Entry 009. No backfill was performed, consistent with the precedent set in Log Entry 006 (the original 8 pre-2000 presence exclusions were also not backfilled; the project accepted N=133 rather than re-sampling to restore a round number). This exclusion is a data availability constraint, not a data quality judgement, and must be described that way in any future documentation (Responsible AI statement, paper Methods section, Data Dictionary).

**Logged by:** Project owner

---

## Log Entry 013 — Pseudo-Absence / Presence Checklist Contradiction: TGB Assumption Violation (3 Records)

**Date:** 2026-08-12 (Phase 3, Milestone 3.11)

**Context:** Milestone 3.11 validation added a cross-class check (grid_cell_id + observation_date pairs appearing in both presence and pseudo-absence records), which had never been run in any prior validation pass. It found exactly one conflicting pair: cell_0079, 2016-01-17, containing 1 confirmed *Quelea quelea* presence record (key 1710848647) and 3 pseudo-absence records (keys 1710847627, 1710847782, 1710848645) drawn from the all-species effort-proxy pool. All four keys are sequential, strongly indicating they originate from a single shared eBird checklist. This is a genuine violation of the Target-Group Background pseudo-absence assumption established in Log Entry 009: a TGB pseudo-absence represents "an observer was present at this location/time and did not detect the target species." That assumption cannot hold for a checklist that demonstrably did detect *Quelea quelea* — the 3 other-species records from that same checklist were incorrectly eligible as absence proxies. This is a gap in the original pseudo-absence pool construction (Log Entry 009), not a new methodology question: standard TGB practice requires excluding effort-proxy records that co-occur with a confirmed target-species detection at the same checklist/location/date, and this exclusion step was missing.

**Decision:** Exclude the 3 contradicting pseudo-absence records from the modelling dataset. Not backfilled, consistent with the precedent in Log Entry 006 and Log Entry 012. `assemble_final_dataset.py`'s output was corrected directly rather than treating this as a scope-level decision requiring sign-off, since the resolution follows unambiguous, standard TGB practice rather than involving a genuine choice between alternatives.

**Impact:** Final modelling dataset size changes from 262 to **259 records**. Class balance changes from 133:129 to **133 presence : 126 pseudo-absence**. Cumulative effect of Log Entry 012 + 013: the originally planned exact 1:1 balance (266 records, Log Entry 009) is now 133:126 (259 records total, ~51.4%/48.6% split) — still close enough to balanced that no class-weighting or resampling is needed for the planned tree-based models. This finding should also inform a durable safeguard: if the pseudo-absence pool is ever regenerated (`build_pseudo_absence_pool.py`, `sample_pseudo_absences.py`), a checklist/date/cell exclusion filter against known presence records should be added at that stage, not discovered again post-hoc during validation.

**Logged by:** Project owner

---

## Log Entry 014 — Pseudo-Absence Month-Concentration Bug: Root Cause, GBIF Pagination Investigation, and Correction

**Date:** 2026-08-12 (Phase 4, Milestone 4.4)

**Context:** EDA (Milestone 4.1) found that 96.8% of pseudo-absence records (122 of 126) fell in January or February, versus 20.3% for presence records — a severe temporal confound that would have let models trivially separate classes by calendar month rather than by environmental suitability, since most rainfall/temperature/dewpoint/NDVI features correlate strongly with season. Root-cause diagnosis traced this to `fetch_effort_pool.py` (the script underlying the original Log Entry 009 pseudo-absence methodology): it queried GBIF's `occurrence/search` endpoint filtered by `year` only, capped at 150 records/year via pagination. Inspection of the raw pool showed several years (2000, 2011, 2012) were literally 150/150 January, and others were heavily January/February-dominated. GBIF's `occurrence/search` endpoint does not publish a guaranteed default sort order; empirically, results returned within a year-only query were overwhelmingly front-loaded from January, and the 150-record cap truncated before reaching other months in years with more data available than the cap. This is structurally the same class of bug as the year-level effort-pool skew already caught and fixed during original pseudo-absence construction (Log Entry 009) — a within-year analog that had gone undetected because no month-level QC had been run on the pool until this EDA pass.

**Investigation of the fix approach:** GBIF's `occurrence/search` API supports an explicit `month` integer parameter (1-12), independent of `year`. Querying by `(year, month)` pairs directly removes any dependency on the endpoint's undocumented internal ordering, rather than working around it. This mirrors the batching pattern already used for ERA5-Land extraction (Log Entry 008, batched by year-month).

**Decision:** Rebuilt the effort-proxy pool via `fetch_effort_pool_v2_month_stratified.py`, querying all 16 presence-spanning years x 12 months (192 queries, ~13 records/pair target). Result: 2,371 records with a genuinely flat month distribution (182-208 per month, max 8.8% concentration, versus 90.7% in a single month previously). While rebuilding, also closed the safeguard gap flagged in Log Entry 013: `build_pseudo_absence_pool_v2.py` now excludes any effort-proxy record sharing a (grid_cell_id, date) pair with a confirmed presence record *before* thinning, rather than relying on post-hoc detection during validation. This excluded 94 records that would otherwise have reintroduced the exact TGB assumption violation found in Milestone 3.11.

**QC performed before proceeding to environmental extraction (per explicit requirement — extraction was deliberately held back pending this verification):**
- Month distribution: presence max 18.8% (November), pseudo-absence max 16.8% (May) — no severe single-month concentration in either class.
- Cross-class contradiction check: 0 (cell, date) pairs shared between presence and pseudo-absence — safeguard confirmed working structurally.
- Year distribution: both classes spread across the full 2000-2026 range, weighted toward 2021-2024 in both (consistent with known eBird growth, not an artifact).
- Spatial coverage: pseudo-absence now spans 81 unique grid cells (up from 49), 8 shared with presence (up from 6) — broader, not narrower, environmental sampling.

**Impact:** All v1 (month-biased) files preserved for traceability: `data/raw/gbif_all_species_effort_pool_v1_month_skewed.csv`, `data/processed/pseudo_absence_pool_v1_month_skewed.csv`, `data/processed/pseudo_absences_final_v1_month_skewed.csv`. The v1-derived final modelling dataset (259 records, validated in Milestone 3.11) is also preserved in full via Git history at commit 4728c6b and must be treated as superseded, not deleted, for reproducibility. **Environmental feature extraction (CHIRPS, ERA5-Land, MODIS NDVI) has NOT yet been re-run for the corrected pseudo-absence set** — record keys changed with the rebuild, so rainfall/meteorology/NDVI features must be freshly extracted for the new 133-record pseudo-absence sample before a new final dataset can be assembled. This is the next task, not yet started as of this log entry.

**Logged by:** Project owner

---

## Log Entry 015 — Ahero/West Kano Rice-Landscape Footprint Investigation; Habitat Predictor Design Decision

**Date:** 2026-10-05 (Phase 5, Level 2 data acquisition)

**Context:** Milestone 2.1's OSM `landuse=farmland` polygons for Ahero (12.33 km2) and West Kano (10.97 km2) were investigated against the Jiang et al. 2025 20m Africa rice distribution raster (Kenya.tif, Zenodo DOI 10.5281/zenodo.13729353, measured pixel size ~10m rather than the paper's documented 20m - a separate, non-blocking discrepancy noted for future documentation). Connected-component analysis of classified rice pixels within a 50km buffer around the Ahero centroid found 451,604 rice pixels (45.16 km2 total), of which only 105,537 (23.4%) fall inside the two named OSM polygons combined. A 3km ring immediately surrounding the Ahero polygon showed rice density dropping sharply (11.12% inside the polygon vs. 4.08% in the adjacent ring), ruling out a simple "polygon is uniformly undersized" explanation. Satellite basemap overlay showed the unclaimed rice mass is largely contiguous with, not disconnected from, the area around both polygons. Reverse-geocoding the ten largest unclaimed patches found most sit within "Ahero Irrigation Scheme sublocation" (an administrative unit distinct from and apparently larger than the small digitized OSM polygon) or Kabonyo Kanyagwal ward (West Kano's own ward); a small residual (~2.3 km2, Kobura ward patches) remains unidentified. An Overpass query for all `landuse=farmland` polygons tagged `operator~"National Irrigation"` within the full buffer returned only the same two polygons already on file; the Overpass query returned only the same two NIA-operated farmland polygons in OSM within the search buffer; therefore, no additional NIA-operated polygon was identified in OSM by this query.

**Evidence summary:**
- *Established:* The OSM scheme polygons for Ahero and West Kano substantially underrepresent the classified rice footprint in their surrounding area.
- *Supported interpretation:* The classified rice footprint substantially exceeds the available OSM farmland polygons for Ahero and West Kano and is predominantly located within areas geographically associated with the broader Ahero-West Kano agricultural landscape. Reverse-geocoding and OSM administrative context support this interpretation, but do not establish authoritative scheme boundaries.
- *Not established:* The authoritative administrative boundary of either scheme. The low rice-fraction inside both named polygons (11.1% Ahero, 18.8% West Kano) is itself unexplained and may indicate incomplete/outdated OSM digitization - flagged, not resolved. The ~2.3 km2 residual in Kobura ward is unattributed to any named scheme.
- *Modeling implication:* Scheme polygons should not be treated as ground-truth habitat boundaries.

**Decision:** For Level 2/3 ecological modeling, do not use binary scheme-membership (inside/outside a named polygon) as a habitat predictor. Instead, represent rice availability continuously using rice proportion/density at multiple spatial scales and distance to nearest rice. Retain the OSM scheme polygons as contextual/geographic metadata for stratification, interpretation and reporting, not as model inputs.

**Candidate predictors (not finalized):** Rice proportion within 500m, 1km, and 2km buffers of each point, and distance to nearest rice pixel, computed directly from the Jiang et al. 2025 raster. These are recorded as candidates for correlation/redundancy and performance assessment during feature engineering, not an assumption that all three scales enter the final model simultaneously.

**Impact:** Supersedes the research_protocol_v2.md framing (already partially retracted by `level2_agricultural_datagap_analysis.md`, Log Entry prior to this one) that treated grid-cell or scheme-boundary membership as a candidate L2-RQ7 predictor. The `within_scheme_boundary` field already present in `analysis_grid.geojson` (Milestone 2/3, 4 of 328 cells flagged) should be treated as contextual/legacy only going forward, not as an ecological predictor, pending any future documentation update.

**Logged by:** Project owner

---

## Log Entry 016 — Rice-Density Predictor Extraction (500m/1km/2km + distance-to-nearest-rice); Pseudo-Absence Representativeness Validation

**Date:** 2026-10-05 (Phase 5, Level 2 data acquisition)

**Context:** Following Entry 015's decision to use continuous rice-landscape variables rather than binary scheme-membership, extracted rice proportion within 500m/1km/2km buffers and distance-to-nearest-rice-pixel for all 266 records (133 presence, 133 pseudo-absence) against the Jiang et al. 2025 raster. Required a prior fix: `modelling_dataset_final.csv` had never carried latitude/longitude through from source files (now fixed; see coordinate-passthrough commit, same session). A spot check (record near Ahero's OSM bbox edge: 14.1% rice at 500m, 259m to nearest rice pixel) and aggregate presence-vs-pseudo-absence contrast (5.78% vs 0.28% mean rice at 2km; ~20x) both support the extraction logic working correctly and a real ecological signal being present.

Per Section 8's required check (deferred from Level 1): compared pseudo-absence rice-density distribution against an independently generated, uniformly-random 266-point spatial sample across the same analysis extent. The pseudo-absence and spatially random samples showed broadly similar rice-exposure distributions, with no strong evidence of systematic background bias. Pseudo-absence was marginally more rice-exposed than the spatially random sample across all four metrics (e.g. 77.4% vs 84.6% with zero rice within 2km, a 7.2 percentage-point difference) - a real, non-negligible divergence, though small relative to the ~20x presence/background contrast.

**Decision:** Proceed with the Entry 015 candidate rice-landscape predictors without additional background-resampling correction. The comparison provides no strong evidence that the pseudo-absence sample has materially different rice exposure from the spatially random background. The modest divergence is retained as a limitation rather than treated as sufficient evidence for correction.

**Candidate predictors (not finalized):** rice_pct_500m, rice_pct_1000m, rice_pct_2000m, dist_to_nearest_rice_m, all extracted and saved (`data/processed/rice_density_features.csv`). As in Entry 015, this validation supports their use as candidates; it does not establish that all spatial scales should enter the final model simultaneously. Correlation/redundancy and model performance to be assessed during feature engineering.

**Limitation:** The pseudo-absence-vs-random comparison is a single random draw (seed=42, n=266) against a single pseudo-absence draw, not a formal bootstrap/distributional test. The conclusion is "no strong evidence of bias," not "proven unbiased." The 7.2 percentage-point zero-rice divergence is unexplained - no observer-accessibility or road-proximity variable was tested, and no causal explanation should be inferred from this analysis alone.

**Logged by:** Project owner

---

## Log Entry 017 — AFCD Temporal Land-Use Stability Cross-Check (Jiang et al. 2025 Rice Snapshot)

**Date:** 2026-10-05 (Phase 5, Level 2 data acquisition)

**Context:** Tested whether Jiang et al. 2025's single 2023 rice-extent snapshot can be reasonably used alongside occurrence/pseudo-absence records spanning observation years 2000-2026 (Feasibility Study Section 4, previously unaddressed). Used AFCD (Lou et al. 2025, annual cropland extent, Zenodo DOI 10.5281/zenodo.14920706, 2000-2022), accessed via GDAL `/vsicurl/` remote windowed reads (confirmed internally tiled, no full-file downloads required). For the 180 records with observation_year <= 2022 (AFCD's coverage ceiling), compared cropland % within a 500m buffer at each record's own observation year against year 2022 (closest AFCD year to the Jiang snapshot). The 86 records with observation_year > 2022 were outside AFCD's 2000-2022 coverage and therefore could not be evaluated using this cross-check. Their temporal distance from the 2023 Jiang snapshot is smaller for 2023-2026 observations, but this does not constitute independent validation.

**Findings:** Strong overall correlation between own-year and 2022 cropland % (r=0.977, n=180), including in the pre-2015 subset specifically flagged as highest-risk by the Feasibility Study's ~2015 satellite rice-mapping ceiling (r=0.960, n=41). Mean absolute difference was 2.45 percentage points but right-skewed (median 0.46pp); the small number of large differences traced to only 6 distinct coordinate locations (several records share exact coordinates across different years), not many independent outliers.

**Decision:** Use the Jiang et al. 2025 2023 rice-extent snapshot as the current rice-landscape representation without per-record temporal correction. The AFCD cropland comparison provides supporting evidence that the broader cropland context was relatively stable across the historical observation period, substantially reducing - but not eliminating - the concern that temporal land-use change is driving the rice-density signal. Proceed with the existing rice-density features (Entry 016) as currently computed.

**Limitation:** AFCD measures generic cropland, not rice specifically - this is a proxy test for broader land-use stability, not direct evidence that the 2023 Jiang rice footprint was representative of rice cover in each historical observation year. The analysis established that the six largest discrepancies are concentrated at 6 distinct coordinate locations, not their cause - no determination was made of whether those changes reflect genuine land-use change, AFCD/Jiang classification disagreement, or edge/mixed-pixel effects. Records from 2023-2026 (n=86) were not tested at all.

**Logged by:** Project owner

---

## Log Entry 018 — Spatial Cross-Validation Fold Design

**Date:** 2026-10-05 (Phase 5, Level 2 data acquisition)

**Context:** Random k-fold cross-validation is inappropriate for this dataset given spatial autocorrelation in ecological point data (Roberts et al. 2017, Ecography 40(8):913-929, DOI 10.1111/ecog.02881; Valavi et al. 2019, Methods in Ecology and Evolution 10(2):225-232, DOI 10.1111/2041-210X.13107) - both establish that block/spatially-separated cross-validation is required to avoid underestimating predictive error when nearby points are split across train/test. This requirement was flagged as outstanding since the original project priority list.

The existing 5.5km grid (328 cells, matched to CHIRPS resolution) was not used as the blocking unit: only 93 of 328 cells are occupied by the 266-record dataset, and occupancy is highly uneven (one cell, `cell_0080`, holds 62 of 266 records - the persistent Winam Gulf site identified in Log Entry 004). Grid-cell blocking at this occupancy pattern risked producing degenerate folds.

**Method:** K-means clustering (k=5, seed=42) was fit on presence-only coordinates to derive 5 geographically meaningful cluster centroids, then every record (presence and pseudo-absence) was assigned to its nearest centroid. This differs from clustering on all points: an initial attempt (v1) clustering on the full point set produced a fold with zero presence records (pure background, unusable for evaluation - precision/recall/F1 undefined), because pseudo-absence points are spread across the full 50km buffer while presence concentrates near rice-scheme and persistent-site locations; whole-dataset clustering could therefore isolate a presence-free geographic region. Anchoring cluster centroids on presence locations specifically eliminates this failure mode by construction.

**Result:**

| Fold | Presence | Pseudo-absence | Total |
|---|---|---|---|
| 0 | 8 | 42 | 50 |
| 1 | 9 | 5 | 14 |
| 2 | 11 | 20 | 31 |
| 3 | 36 | 22 | 58 |
| 4 | 69 | 44 | 113 |

No fold has zero of either class. Fold sizes are uneven (Fold 4 at 113, anchored on the `cell_0080` persistent-site cluster; Fold 1 at 14) - this is treated as an expected consequence of genuine spatial blocking, not corrected toward artificial balance, consistent with both cited sources treatment of block CV.

**Verification:** All 62 records from `cell_0080` were assigned to Fold 4 and therefore were not split across folds. One grid cell (`cell_0098`, 2 pseudo-absence records) was split across two folds; the two records are separated by 4.622km, which exceeds the maximum 2km radius of the current rice-density features (Entry 016), so the two records do not share the same rice-density feature neighbourhood at the largest extraction scale. This does not rule out other forms of spatial autocorrelation. Separately, `data/processed/spatial_cv_folds.csv` was verified against the current 266-record `modelling_dataset_final.csv`: exact 1:1 record coverage with no duplicates or omissions, exactly 5 fold IDs, every fold containing at least one record of each class, and zero mismatches on an independent re-run using the same dataset and KMeans configuration, confirming reproducibility.

**Decision:** Use these presence-anchored k-means folds (`data/processed/spatial_cv_folds.csv`) for all model evaluation going forward. Do not use random k-fold cross-validation for this dataset.

**Limitation:** Fold 1 is small (n=14); performance estimates on this fold specifically will be high-variance. Fold sizes reflect genuine spatial structure rather than a deliberately balanced design, and this should be disclosed alongside any cross-validated metric reported from this scheme.

**Logged by:** Project owner

---

## Log Entry 019 — Baseline Predictor Selection

**Date:** 2026-10-05 (Phase 5, Level 2 data acquisition)

**Context:** Before training the baseline model, checked pairwise correlation across candidate predictor groups to inform feature selection rather than including all 29 columns by default, given the dataset's limited size (266 records, 133 presence) and uneven spatial fold structure (Entry 018; Fold 1 at n=14, with only 9 presence and 5 pseudo-absence).

**Correlation findings:**
- Rice-density buffer scales are highly collinear: 500m/1000m/2000m pairwise correlations 0.94-0.98. `dist_to_nearest_rice_m` is comparatively distinct (-0.42 to -0.50 vs. the density measures).
- Meteorology same-day and 7-day-mean variables are near-duplicates for temp (r=0.90) and dewpoint (r=0.89); wind is more moderate (r=0.64).
- Rainfall windows are partially redundant: 7d-30d at r=0.72, but 90d is comparatively distinct from both (r=0.30, 0.52).
- NDVI composite and anomaly are correlated (r=0.79) but conceptually distinct (absolute greenness vs. deviation from seasonal norm).
- Terrain/hydrology variables (elevation, slope, distance-to-water) are at most moderately correlated (r<=0.62); no redundancy concern.

**Decision - baseline predictor set (10 numeric + season categorical):**

| Category | Included | Deferred |
|---|---|---|
| Rice-landscape | `rice_pct_1000m` (intermediate scale), `dist_to_nearest_rice_m` (distinct proximity signal) | `rice_pct_500m`, `rice_pct_2000m` |
| Rainfall | `rainfall_30d` | `rainfall_7d`, `rainfall_90d` |
| Meteorology | `temp_mean_7d`, `dewpoint_mean_7d`, `wind_mean_7d` | same-day equivalents |
| Vegetation | `ndvi_nearest_composite` | `ndvi_anomaly` |
| Terrain/hydrology | `elevation_m`, `slope_deg`, `dist_to_water_m` | - |
| Temporal | `season` (categorical) | `month`, `day_of_year` |

`ndvi_anomaly` is deferred as a deliberate parsimony choice, not because its correlation with `ndvi_nearest_composite` (r=0.79) by itself proves redundancy. Deferred features (`rice_pct_500m`, `rice_pct_2000m`, same-day meteorology, `ndvi_anomaly`) remain candidates for a later advanced/regularized model where collinearity is less consequential - they are not permanently rejected.

**Deliberately excluded (not deferred):** `latitude`/`longitude` - including raw coordinates would let the model learn spatial position directly rather than environmental association, undermining the purpose of testing environmental predictors, and risks the model memorizing fold-specific spatial clusters given how concentrated this dataset is. `within_scheme_boundary` remains excluded per Entry 015.

**Limitation:** The compact 10-predictor baseline is a deliberate parsimony choice given the dataset's size and structure, not a claim that sample size is demonstrably adequate for this predictor count. The dataset's effective independence is constrained by both its small total size (133 presence records) and its spatial fold structure (Entry 018); Fold 1 in particular (9 presence, 5 pseudo-absence) will yield high-variance per-fold estimates regardless of predictor count. This should be disclosed alongside any baseline performance metric, not treated as resolved by the feature-selection choices made here.

**Logged by:** Project owner

---

## Log Entry 020 — Baseline Logistic Regression: Spatial-CV Results, Diagnostics and Evidential Limits

**Date:** 2026-11-02 (document date; the Git commit timestamp is the verifiable record). The baseline run preceded this entry and its own date is not recorded in the repository.

**Context:** First model training on the 266-record modelling dataset (`data/processed/modelling_dataset_final.csv`, Git blob 60e1fd7654bc20322fdc2c00c32a2ef95d117a87), using the predictor set from Entry 019 (10 numeric predictors plus `season`, one-hot encoded with `dry_cool` as the reference level; 13 model columns) and leave-one-fold-out evaluation on the five spatial folds from Entry 018 (`data/processed/spatial_cv_folds.csv`). Model: scikit-learn `LogisticRegression` (`max_iter=1000`, `random_state=42`, otherwise default settings: L2 penalty, C=1.0, no class weighting, 0.5 decision threshold). Numeric predictors were standardised with a `StandardScaler` fit on the training folds only in each iteration. This is a benchmark model; no hyperparameter or threshold tuning was performed. Library versions were not recorded for this run. Artefacts: `src/train_baseline_logistic_regression.py`, `src/diagnose_baseline_calibration.py`, `src/diagnose_fold4_persistent_site.py`, `reports/baseline_logistic_regression_cv_results.csv`. Before they were committed the artefacts were verified: the script byte counts were reproduced exactly from their contents, and the per-fold results file matches the printed metrics at three decimals (`n_test` sums to 266 and `n_presence_test` to 133).

**Results (held-out fold):**

| Test fold | n | Presence | Precision | Recall | F1 | ROC-AUC | Confusion matrix [[TN, FP], [FN, TP]] |
|---|---|---|---|---|---|---|---|
| 0 | 50 | 8 | 1.000 | 0.125 | 0.222 | 0.961 | [[42, 0], [7, 1]] |
| 1 | 14 | 9 | 0.700 | 0.778 | 0.737 | 0.867 | [[2, 3], [2, 7]] |
| 2 | 31 | 11 | 0.500 | 0.909 | 0.645 | 0.718 | [[10, 10], [1, 10]] |
| 3 | 58 | 36 | 0.882 | 0.833 | 0.857 | 0.886 | [[18, 4], [6, 30]] |
| 4 | 113 | 69 | 0.833 | 0.362 | 0.505 | 0.839 | [[39, 5], [44, 25]] |

Unweighted mean (sample SD) across the five folds: precision 0.783 (0.191), recall 0.602 (0.340), F1 0.593 (0.244), ROC-AUC 0.854 (0.089). Fold sizes range from 14 to 113 records, so the unweighted mean gives Fold 1 the same weight as Fold 4. Fold 0's precision of 1.000 rests on a single positive prediction.

**Effective sample size by test fold:**

| Test fold | Presence records | Distinct presence coordinates | Presence-bearing cells | Distinct presence (coordinate, date) vectors | Background records | Distinct background (coordinate, date) vectors |
|---|---|---|---|---|---|---|
| 0 | 8 | 5 | 4 | 5 | 42 | 37 |
| 1 | 9 | 2 | 2 | 6 | 5 | 4 |
| 2 | 11 | 6 | 5 | 10 | 20 | 15 |
| 3 | 36 | 9 | 6 | 24 | 22 | 16 |
| 4 | 69 | 7 | 3 | 41 | 44 | 37 |
| All | 133 | 29 | 20 | 86 | 133 | 109 |

Two cells hold 87 of the 133 presences (65.4%): `cell_0080` (60 presences, all in Fold 4) and `cell_0156` (27, all in Fold 3). Fold 4's presences are 87% `cell_0080` and Fold 3's are 75% `cell_0156`. Forty-seven presence records repeat another presence record's coordinate and date and so have identical baseline predictor values.

**Diagnostics.** Predicted-probability level by test fold (`src/diagnose_baseline_calibration.py`). The "test presence rate" is a property of the sampling design (1:1 background, nearest-centroid fold assignment), not an estimate of prevalence:

| Test fold | Training-fold presence rate | Test-fold presence rate | Mean predicted probability (test) | Fraction predicted positive at 0.5 |
|---|---|---|---|---|
| 0 | 0.579 | 0.160 | 0.053 | 0.020 |
| 1 | 0.492 | 0.643 | 0.750 | 0.714 |
| 2 | 0.519 | 0.355 | 0.517 | 0.645 |
| 3 | 0.466 | 0.621 | 0.539 | 0.586 |
| 4 | 0.418 | 0.611 | 0.341 | 0.265 |

Threshold-dependent metrics vary widely across folds (recall 0.125-0.909) and the level of predicted probabilities departs from each fold's sample presence rate in different directions (lower in Folds 0 and 4, higher in Folds 1 and 2). A simple training/test base-rate mismatch does not account for the direction of the error: Fold 0 was trained on a presence-heavy set (57.9%) yet predicts low probabilities on its test fold.

Fold 4 follow-up (`src/diagnose_fold4_persistent_site.py`): 60 of Fold 4's 113 test records are presences from `cell_0080`. In that fold 35.0% of those 60 presences were predicted positive at 0.5 (mean predicted probability 0.431), against 44.4% of the 9 other presences (mean 0.508); 39 of the fold's 44 false negatives (derived from the reported fractions) are `cell_0080` presences. The 42 non-`cell_0080` background records had a mean predicted probability of 0.164 and 9.5% predicted positive. The two `cell_0080` background records averaged 0.568, which is not interpretable at n=2.

**ROC-AUC.** ROC-AUC (0.718-0.961 across folds) varied less than recall (0.125-0.909). That is a descriptive observation and not evidence that ROC-AUC is the preferred or more trustworthy metric here: it is rank-based and ignores predicted-probability level (Lobo et al. 2008, Global Ecology and Biogeography 17(2):145-151); per-fold values rest on few independent sites (Folds 3 and 4 are dominated by one cell each); the negatives are pseudo-absences, so what ROC-AUC measures depends on the background design and the extent evaluated (Jimenez-Valverde 2012, Global Ecology and Biogeography 21(4):498-507; Lobo et al. 2008); and the cross-fold SD is not a standard error because the five fits share most of their training data and the folds are very unequal. The metric designation in Technical Architecture Section 9 (F1, precision and recall primary; ROC-AUC secondary) is unchanged.

**Status of findings:**
- *Established:* the per-fold metrics, confusion matrices and probability-level figures above; the concentration of presences in two cells; most of Fold 4's false negatives come from a single grid cell.
- *Not established:* why predicted-probability levels differ by region; whether the 60 `cell_0080` presences in the training data influence the fits used for the other folds; whether predictor-presence relationships differ regionally. None of these was tested.

**Decision:** Treat this model as a benchmark only. No threshold tuning, class weighting or other change is made to it. Threshold-dependent metrics from this scheme are reported per fold, with fold sizes and distinct-site counts, and not as a single pooled figure. No headline metric is designated. The audit of what this evaluation can and cannot support is pre-specified in Entry 023; it is not intended to improve the scores.

**Limitation:** The folds are contiguous regions of one landscape and share years; the results cannot support claims about other regions, forecasting over time, site-level generality, absolute probability, or infestation. The background is a single draw of other-species records, so "absence" is never observed absence. Fold sizes are small and uneven, and the unweighted fold mean is not a pooled estimate.

**Logged by:** Project owner

---

## Log Entry 021 — Entry 009 Presence-Thinning Statement: Decision-History Review (Original Intent Unresolved)

**Date:** 2026-11-02 (document date; the Git commit timestamp is the verifiable record)

**Context:** Entry 009 (Git timestamp 2026-08-03T22:30:54+03:00, commit 651b520) lists spatial thinning of presences as adopted and names `cell_0080` and `cell_0156`. The modelling dataset retains all 133 presences, including 60 in `cell_0080` and 27 in `cell_0156`. The decision history was reviewed from repository contents (files, history and commit messages) to establish whether thinning was intended, revised or abandoned.

**Established from the repository:**
- Entry 009 contains three relevant statements, unchanged since commit 651b520: (a) a strategy-table row "Spatial thinning of presences (STSP)" with the rationale "directly relevant to cell_0080/cell_0156 concentration" and the verdict "Yes (combined with TGB, not standalone)"; (b) a decision sentence combining approximate TGB sampling with "light spatial thinning to avoid over-concentration at known hotspots (cell_0080, cell_0156)"; (c) a next-steps sentence listing "spatial thinning" among the implementation steps. No thinning rule (distance or per-cell cap) and no pipeline stage is specified for presences.
- Thinning code (`MAX_PER_CELL = 5`) first appears in commit 5795792 (2026-08-04) and is applied to the effort-proxy background pool. The Milestone 3.9 report records "After spatial thinning (max 5 per grid cell): 196" for that pool. No script in the current repository, and none in its history (no file under `src/` was ever deleted), thins the presence set.
- Entry 006 states that the 161-record raw and 145-record grid-matched datasets are retained in full, and defines the 133 presences on or after January 2000 as "feature-complete modelling dataset candidates". Entry 004 states "No methodology change results from this entry". Entry 010 describes the pseudo-absence set as 133 records at a 1:1 ratio with presences and does not mention presence thinning.
- No later entry, commit message, document or report records presence thinning being applied, revised or abandoned. `docs/engineering_log.md` (commit 1b868ba, 2026-08-14T01:22:27+03:00) restates "light spatial thinning" without saying what was thinned, and separately lists the `cell_0080`/`cell_0156` concentration as an open warning ("Random record-level splitting could leak site-specific information across train/test partitions"). Entry 018 addressed leakage through spatial folds, not thinning.

**Not established:** whether Entry 009's statement was intended to apply to presences, to the background pool, or to both; whether it was later revised or abandoned. The original intent is recorded as unresolved unless further evidence emerges. This entry does not interpret or rewrite the historical decision.

**Decision:** No change is made to the dataset. The current dataset contains no presence thinning. Any future thinning, weighting or grouped-validation change would be a separate logged decision with its own scientific justification. The CV audit pre-specified in Entry 023 examines how the baseline results depend on the concentrated cells without altering the dataset.

**Limitation:** The review covers the repository only; material outside it (for example earlier working notes) was not available.

**Logged by:** Project owner

---

## Log Entry 022 — Document Dates Versus Git Timestamps (Entries 014-019 and Phase Labels)

**Date:** 2026-11-02 (document date; the Git commit timestamp is the verifiable record)

**Context:** A mismatch was found between the `Date:` lines of some entries and the Git timestamps of the commits that introduced them. This entry records the facts. It does not alter past entries and does not infer authoring dates.

| Entry | Document `Date:` line | Commit | Git timestamp (author = committer) |
|---|---|---|---|
| 014 | 2026-08-12 | 22151ff | 2026-08-13T13:12:34+03:00 |
| 015 | 2026-10-05 | ca133e4 | 2026-10-05T04:03:18+03:00 |
| 016 | 2026-10-05 | ca3b72e | 2026-10-05T11:58:56+03:00 |
| 017 | 2026-10-05 | aafefad | 2026-10-07T08:46:24+03:00 |
| 018 | 2026-10-05 | cdf2819 | 2026-10-07T09:34:33+03:00 |
| 019 | 2026-10-05 | 9e89f89 | 2026-10-07T10:00:06+03:00 |

**Observations:**
- The document date precedes the commit date by one day for Entry 014 and by two days for Entries 017-019; Entries 015 and 016 were committed on their stated date. Whether the text was written on the stated dates cannot be verified from the repository, because a Git timestamp shows when text was committed, not when it was written.
- Author and committer timestamps are identical in all six commits, so there is no sign of amendment or rebase.
- Entry 017 was committed together with the attribution-wording cleanup of the decision log (commit aafefad).
- The `Date:` lines of Entries 015-019 carry the label "(Phase 5, Level 2 data acquisition)". `docs/implementation_roadmap.md` defines Phase 5 as "Evaluation", and "Level 2 data acquisition" is not a defined phase label, so the parenthetical does not correspond to a documented project phase. Entries 009-014 use roadmap labels (for example "Phase 3, Milestone 3.9").

**Decision:** Past `Date:` lines and labels are left unedited. From Entry 020 onward, `Date:` lines are labelled as document dates and the Git commit timestamp is treated as the verifiable record. If the original dates can later be established from evidence outside the repository (for example local file timestamps), the correction will be made in a separate logged entry.

**Logged by:** Project owner

---

## Log Entry 023 — Pre-Specification: CV Audit Protocol v1.2 (Frozen)

**Date:** 2026-11-02 (document date; the Git commit timestamp is the verifiable record)

**Context:** An audit of the baseline spatial-CV evaluation (Entries 018-020) was designed to establish what the existing analysis can and cannot support. It is not intended to improve scores or to select a model. The frozen protocol is stored as `docs/cv_audit_protocol_v1_2.md` (Git blob b569741912a4bc20465bdb031cf68de60bfe1494, 31,772 bytes; an ASCII rendering of the approved text with symbols spelled out). It is not edited in place; any change requires a new logged version.

**Predeclared elements (summary; the protocol file is authoritative):**
- Four analysis classes kept separate: D (data-only descriptive, D1-D7), M0 (re-execution of the baseline with an identical specification and a reproduction gate), R (re-scoring of fixed M0 predictions, R1-R5) and M1 (training-composition refits: exact-repeat weighting V1, cell-balanced weighting V2, ablation V3 of all records in a cell, and four reference ablations). Order: D, M0, R, M1.
- Banded Moran's I: bands 0-1, 1-2, 2-5, 5-10, 10-20, 20-40, 40-80 and 80-120 km; global binary weights; a minimum of 30 pairs per band as an operational threshold, not a statistical standard; all band counts printed whether or not the minimum is met.
- D6 Mahalanobis distance to the training-distribution centroid is "not estimable" if a predictor has zero variance among the distinct training vectors, if there are fewer than 11 such vectors, or if the condition number of their correlation matrix exceeds 1e8; no regularisation and no dropped predictors.
- M0 identity gates: dataset blob 60e1fd7654bc20322fdc2c00c32a2ef95d117a87, fold file blob 67d8fec7c2b7aab6e98035cc8c916baf826338d0, pseudo-absence source blob 0b617c9f90d42c692c711a5d95a700cb585396ab, the exact 29-column list, an explicit `dry_cool` reference encoding, and numerical tolerances (counts exact; precision, recall and F1 within 1e-12; AUC within 1e-9) with a stop rule on any discrepancy.
- Outputs are write-once under `reports/cv_audit/` with per-run manifests, and no existing artefact is modified.
- No hypothesis tests, no required confidence intervals and no headline metric. All predeclared results are reported, including null, adverse and not-estimable results. Weighting is not treated as a correction for sampling bias or dependence.

**Information available when the protocol was frozen (disclosure):** The protocol was written after the baseline results and the Fold 4 diagnostics (Entry 020) were known, so it pre-specifies the audit analyses and not the baseline. During design, descriptive tabulations were computed in an exploratory scratch environment: per-fold records, distinct coordinates, grid cells and distinct (coordinate, date) vectors; the composition of `cell_0080` and `cell_0156`; year-by-fold counts and dates shared across folds; and the fold membership of the cells used in the ablations. These counts informed the design and are recomputed formally in D1, D5 and D7. No D2, D3, D4 or D6 statistic, no output of an M0 re-execution, and no R or M1 result existed when the protocol was frozen; in particular no Moran's I value and no condition number had been computed.

**Decision:** Execute the audit exactly as specified and in the stated order. Any deviation, including any change to a predeclared threshold, will be logged as a deviation with its reason.

**Limitation:** The audit describes the evidential strength of the existing analysis. It cannot establish that the fold design is adequate, correct sampling bias, or create independent information, and it makes no claim beyond the scope stated in Section 2 of the protocol.

**Logged by:** Project owner

---

## Log Entry 024 - CV Audit Stage D: Data-Only Descriptive Results, D4 Mapping Decision and Interpretation Limits

**Date:** 2026-11-12 (document date; the Git commit timestamp is the verifiable record)

**Context:** Stage D of the frozen CV Audit Protocol v1.2 (Entry 023) was executed twice on the project owner's machine (two write-once run directories, see Repeated execution), as analyses D1-D7 with no model and no predictions. The scripts were committed first as 05b7a935353447eb5e2834c56e2473cdc72be2bf (`src/cv_audit_common.py`, blob fe650f301938dd58ee3dc3cb615c2275a5569c4e; `src/cv_audit_d.py`, blob e56ee8ae9839bc3c09d5c107763995d0ad445e1f). The later run wrote 22 files to `reports/cv_audit/D_20261112T084903Z_05b7a93/`, including `manifest.json` (HEAD, script blobs, library versions, parameters and 32 assertions). In each run all 32 assertions passed: the three gated blobs, the protocol blob at HEAD and in the working copy, the 29-column list, 266 rows, 133/133 classes, no missing cells, fold-file identity, per-fold class counts, key linkage to the pseudo-absence and occurrence files, the frozen D1 and D7 counts, and unchanged SHA-256 hashes of all protected inputs and existing audit files before and after the run.

**Repeated execution:** The D script was run twice at the same HEAD (05b7a935353447eb5e2834c56e2473cdc72be2bf) with the same script blobs. The first run is `reports/cv_audit/D_20261111T201804Z_05b7a93/` (started 2026-11-11T20:18:04Z, finished 20:18:08Z, 22 files, 32 of 32 assertions passed, no earlier audit files to hash). The second is `reports/cv_audit/D_20261112T084903Z_05b7a93/` (started 2026-11-12T08:49:03Z, finished 08:49:13Z, 22 files, 32 of 32 assertions passed, the first run's 22 files hashed before and after the run and unchanged). The two directories were compared by SHA-256: the 20 data files are byte-identical, and `run_summary.txt` is identical after its first line; `manifest.json` and that first line name the run and its time and were excluded from the comparison. The reason for the second execution is not recorded here. The printed output reviewed for this entry came from the second run. Both directories are kept, because outputs are write-once and nothing is deleted. Identical results show that stage D is deterministic on these inputs, on this machine and with these library versions; they are not independent confirmation, because both runs used the same code and data.

**Testing disclosure:** After the protocol was frozen and committed, the scripts were developed and tested in an exploratory scratch environment on the committed inputs, and the scratch run reproduced the official run's printed output. Scratch outputs are development only; every result below is from the official runs (see Repeated execution). No predeclared band, threshold, rule or parameter was changed after any scratch output was seen.

**Implementation decisions within the frozen wording:**
- Distinct vector: a distinct row of the ten numeric baseline predictors (exact equality of stored values), identified by `vector_id`. D1 and D7 reproduced the frozen counts, with 86 distinct presence vectors and 109 distinct background vectors.
- D4 grid definitions: the extraction code computes each grid-cell centroid in EPSG:32736 and converts it to EPSG:4326 (`extract_rainfall_from_cache.py`, `extract_meteorology_features.py`), and rainfall and meteorology are read at that centroid, not at the record's own coordinates (Entry 002, unit of analysis). D4 therefore maps each analysis cell, not each record, to a CHIRPS pixel and an ERA5-Land grid point. The CHIRPS pixel uses the documented global 0.05 degree grid with origin (-180, 50), because no cached CHIRPS raster was found at run time. The ERA5-Land point is the nearest point on a 0.1 degree lattice, the same nearest-point rule the extraction used; the lattice was not read from a downloaded file. Status of both mappings: proposed (documented grids, not verified against the original files). The earlier ERDDAP-based script `extract_rainfall_features.py` computes centroids in geographic coordinates and was not used as the reference; which script produced the committed rainfall file was not checked in this stage, and the NDVI, terrain and hydrology extraction code was not re-read.
- D3a: the five static predictors use one value per distinct coordinate; the five dynamic predictors use one value per distinct (coordinate, date) vector with same-date pairs only; strata are all, presence and background. The output adds, for each band, the number of pairs lying inside one analysis cell.
- The manifest field `git_status_short` is captured when the run is finalised, after the run directory exists, so its value (`?? reports/cv_audit/`) describes the run's own output and not the state when the run started.

**Results (established = computed from the committed data by the audit code in the official run):**
- D1 and D7 (established): every frozen count reproduced. Presence records 8/9/11/36/69, distinct presence coordinates 5/2/6/9/7, presence cells 4/2/5/6/3 and distinct presence vectors 5/6/10/24/41 per fold (totals 133, 29, 20 and 86). `cell_0080` holds 60 presences and 2 background records in Fold 4 (34 presence dates, years 2011-2024, 32 presences in 2023-2024). `cell_0156` holds 27 presences and no background in Fold 3. The two cells hold 87 of 133 presences. 47 presence records repeat another record's coordinate and date. Background per fold: records 42/5/20/22/44, distinct vectors 37/4/15/16/37, distinct coordinates 34/4/15/14/36, cells 26/4/11/13/28.
- D2 (established, descriptive only): held-out presence records lie between 3.785 km (Fold 4) and 29.686 km (Fold 2) from the nearest training record, and between 6.121 km and 29.686 km from the nearest training presence. Median nearest-training-record distance per fold (record unit): 14.193, 6.121, 25.602, 10.979 and 6.454 km for Folds 0-4. Fold 4's record-level values run from a 6.454 km median to a 6.456 km maximum because its 69 presence records sit at 7 distinct coordinates; at the distinct-coordinate unit its median is 5.272 km. No threshold is applied and no fold is classified as independent or contaminated.
- D3b (established): the 29 presence coordinates have nearest-neighbour distances with minimum 0.063, median 2.267 and maximum 22.264 km. 25 have their nearest neighbour in the same fold and 4 in another fold. The 406 pairs split into 83 within-fold and 323 cross-fold. These distances reflect observation sites and observer effort, not ecological aggregation.
- D3a counts (established): pairs per band (0-1, 1-2, 2-5, 5-10, 10-20, 20-40, 40-80, 80-120 km): all strata 24, 19, 113, 279, 774, 2222, 3839, 731; presence 9, 5, 21, 32, 83, 155, 100, 1; background 10, 10, 65, 190, 488, 1343, 2513, 634. 80 of the 120 static rows meet the predeclared 30-pair rule (all: 6 of 8 bands; presence: 4 of 8, the 5-80 km bands; background: 6 of 8). None of the 120 dynamic rows does: the most same-date pairs in any band are 3 (all), 2 (presence) and 1 (background). In the presence stratum the largest single-point share of a band's pairs is 0.333, 0.400, 0.238, 0.281, 0.133, 0.116, 0.210 and 1.000 (the single pair in 80-120 km). In the all stratum, 18 of 24, 15 of 19 and 18 of 113 pairs in the three bands below 5 km lie inside one analysis cell, and none do above 5 km.
- D3a values (computed under the predeclared rule): in the all stratum the five static predictors are positive in the 2-5, 5-10 and 10-20 km bands (elevation_m 1.084, 0.977, 0.756; dist_to_nearest_rice_m 0.619, 0.594, 0.412; rice_pct_1000m 0.660, 0.376, 0.089; dist_to_water_m 0.462, 0.090, 0.174; slope_deg 0.464, 0.235, 0.229) and lie between -0.357 and 0.165 from 20 km upward (elevation_m -0.311 and -0.357 in the 40-80 and 80-120 km bands). The background stratum shows the same pattern for elevation_m (1.074, 0.963, 0.668 at 2-20 km). In the presence stratum, in the 5-80 km bands, elevation_m is 0.193, 0.305, -0.063 and -0.456, dist_to_nearest_rice_m is 0.273, 0.093, -0.212 and -0.272, and the other three predictors lie between -0.219 and 0.168.
- D4 (established, conditional on the proposed mappings): no held-out presence record shares an analysis cell or CHIRPS pixel with a training record. One background record each in Fold 1 (1 of 5) and Fold 4 (1 of 44) shares a cell and pixel with a training record, on a different date. ERA5-Land point sharing with training records, held-out presences: Fold 0 2 of 8 records, Fold 1 7 of 9, Fold 2 0 of 11, Fold 3 2 of 36, Fold 4 0 of 69; held-out background: shares of 0.095, 0.400, 0.000, 0.455 and 0.114 for Folds 0-4. Training records at the same ERA5-Land point and on the same date (identical meteorology) exist for 1 Fold 0 presence record and 1 Fold 3 presence record, and for no background record. Mapping check: 48 groups of records share an analysis cell and a date and show no differing value in any dynamic predictor; 48 groups share a CHIRPS pixel and date, none spanning more than one analysis cell, so the CHIRPS pixel mapping is not tested by this check; 49 groups share an ERA5-Land point and date, 2 of them spanning two analysis cells, with no differing value (consistent with the mapping, but only two cross-cell groups). Shared inputs are not proof of leakage.
- D5 (established): 180 distinct dates, 6 of them in more than one fold (2019-11-28 in Folds 0 and 3; 2021-07-11 in 1 and 3; 2021-10-09 in 0 and 2; 2021-11-06, 2023-04-06 and 2023-08-28 each in 3 and 4), covering 16 records. Year ranges per fold: 2001-2026, 2012-2024, 2012-2026, 2000-2026 and 2001-2026. The folds are spatial, not temporal, and no temporal claim follows.
- D6 (established): share of held-out records outside the training min-max range on at least one of the ten predictors, Folds 0-4: 14 of 50 (0.280), 7 of 14 (0.500), 2 of 31 (0.065), 16 of 58 (0.276) and 7 of 113 (0.062). The predictors involved: Fold 0 elevation_m (9 records); Fold 1 dist_to_water_m (7 records); Fold 3 dist_to_water_m (7), dist_to_nearest_rice_m (4) and temp_mean_7d (4); Fold 4 wind_mean_7d (4) and ndvi_nearest_composite (3). The Mahalanobis distance to the training-distribution centroid is estimable for every fold (distinct training vectors 153, 185, 170, 155, 117; kappa_2(R) 38.7, 49.2, 53.3, 49.8, 60.8 against the 1e8 limit; lambda_min 0.090, 0.068, 0.066, 0.065, 0.063). Median record distance per fold: 5.058, 5.871, 2.568, 3.720 and 3.066. By class (presence / background median): Fold 0 3.105 / 5.319; Fold 1 8.152 / 3.194; Fold 2 2.635 / 2.297; Fold 3 3.766 / 3.683; Fold 4 3.148 / 3.036. No threshold is applied. Out-of-range does not imply poor prediction.

**Interpretation limits:**
- D3a describes the predictors, not model residuals or the species; residual autocorrelation is analysed in R5. Terrain and hydrology predictors are identical within an analysis cell by construction, so within-cell pairs inflate the short-distance bands for those predictors (the rice predictors are coordinate-level and are not affected by that mechanism). With global binary weights the statistic is not bounded by 1 (elevation_m 1.084), pairs share points, and single points can account for large shares of a band's pairs, so values are descriptive and not precise estimates.
- Comparing the D2 distances with the D3a bands is not a protocol analysis. Both are reported; no conclusion about fold independence is drawn from them.
- D6 Mahalanobis values depend on a sample covariance estimated from 117-185 distinct vectors in 10 dimensions, and Fold 1 has only 14 test records (10 distinct vectors).
- The CHIRPS and ERA5-Land mappings in D4 are proposed (see implementation decisions), and the D4 counts are conditional on them.

**Observations carried forward as hypotheses (not tested in D):**
- Hypothesis: spatial blocking at the present fold scale does not remove predictor-level spatial structure between folds, because positive autocorrelation of several predictors is computed at 2-20 km while held-out presences lie 3.8-29.7 km from the nearest training record. Tested directly only by residual autocorrelation (R5) and by the M0/R/M1 stages.
- Hypothesis: Fold 4's 44 false negatives (Entry 020) are not explained by marginal extrapolation, since only 7 of its 113 test records are outside the training range and its Mahalanobis medians are close to the other folds'. Fold 0's presences are nearer the training centroid than its background (3.105 versus 5.319), so its low recall is also not obviously a distance effect. Both are observations about D outputs only; they are examined in R and M1.

**What stage D does not establish:** that any fold is independent or contaminated; that the fold design is adequate; that shared coarse inputs caused any score; that predictor autocorrelation transfers to model errors; or that any out-of-range share explains baseline performance. It creates no independent information and selects no model.

**Decision:** Commit both D run directories (44 files) and this entry unchanged and proceed to M0 under the frozen protocol. No predeclared parameter was changed. The CHIRPS and ERA5-Land mappings stay marked as proposed until they can be checked against the original grids. Nothing in this entry is used to choose a model or to tune the baseline.

**Logged by:** Project owner

---
