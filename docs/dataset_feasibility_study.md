# Dataset Feasibility Study & Inventory

**Project:** QueleaGuard
**Phase:** 2 — Research & Dataset Discovery
**Version:** 1.0
**Status:** Finalized for Phase 2 Planning — implementation validation (Milestone 2.1 onward) still pending

---

# 1. Purpose

This document catalogues every dataset QueleaGuard may require, assesses whether each is realistically obtainable, and evaluates whether they can be honestly combined into a single machine-learning-ready dataset. It is the authoritative reference for data strategy decisions going into Phase 2 implementation. Items marked **[UNVERIFIED]** require an empirical check before being treated as settled - those checks are Phase 2's implementation milestones, tracked in Section 9.

---

# 2. Dataset Catalogue

## 2.1 Bird Occurrence Data

### GBIF (Global Biodiversity Information Facility)

| Attribute | Detail |
|---|---|
| Contents | Point occurrence records (species, date, lat/lon, coordinate uncertainty, basis of record) aggregated from museums, citizen science, and research datasets, including eBird-derived records republished through GBIF |
| Why needed | Source of the target variable - historical Quelea quelea sightings |
| Public availability | Yes - free, via web download or rgbif/pygbif API |
| Licensing | CC0, CC-BY, or CC-BY-NC depending on constituent dataset; GBIF aggregates records from multiple publishers, each with its own license - must check per-download |
| Spatial resolution | Point coordinates; coordinate uncertainty varies widely per record (some precise to meters, others to tens of km) - this field must be filtered on, not ignored |
| Temporal resolution | Per-record date (day-level where reported; some historical records only have year/month) |
| Expected format | CSV or Darwin Core Archive (DwC-A) |
| Preprocessing | Filter by species, bounding box, coordinate uncertainty threshold, and basis-of-record type; deduplicate; flag/exclude fossil or unreliable-source records |
| Limitations | [UNVERIFIED] - record density in a bounding box around two small irrigation schemes is unknown until queried. GBIF is also presence-only: it records where quelea were seen, not where they were absent, and observation effort is spatially biased toward accessible/popular birding sites |

### eBird (Cornell Lab of Ornithology)

| Attribute | Detail |
|---|---|
| Contents | Citizen-science bird checklists, including complete-checklist "effort" metadata (distance, duration, observer count) |
| Why needed | Denser coverage than GBIF in many regions, and - critically - eBird's complete checklists allow construction of true absences (a checklist that didn't report quelea, at a known effort level, is a real negative, unlike GBIF's silence) |
| Public availability | Partial. Basic observations flow into GBIF already. The full eBird Basic Dataset (EBD), which includes checklist-level effort data needed for proper absence modeling, requires a free account and a data-use request via ebird.org - not an instant API pull |
| Licensing | eBird Terms of Use - non-commercial research/education use permitted, redistribution restricted |
| Spatial resolution | Point coordinates (hotspot or personal location) |
| Temporal resolution | Day-level, with time-of-day |
| Expected format | Tab-delimited EBD text file (can be tens of GB unfiltered - must filter by region/species at request time) |
| Preprocessing | Filter to Kenya/study region and target species/date range at request time; parse checklist effort fields for absence construction |
| Limitations | Access lead time (request approval isn't instant); still subject to observer-effort bias, though less severe than GBIF alone since effort is quantified |

**Assessment:** GBIF is the fast, low-friction source to check feasibility first. eBird's EBD is the stronger long-term source specifically because it supports defensible absence construction - worth requesting in parallel once GBIF's density check clarifies whether the project is data-constrained.

---

## 2.2 Climate Data

### CHIRPS (rainfall only)

| Attribute | Detail |
|---|---|
| Contents | Gridded daily/pentad/monthly rainfall estimates, blending satellite infrared and station data |
| Why needed | Rainfall is a well-documented driver of quelea breeding and movement (breeding is cued by green vegetation flush following rain) |
| Public availability | Yes - free via CHC-UCSB, Climate Serv, or Digital Earth Africa (Africa-specific mirror) |
| Licensing | Public domain / open |
| Spatial resolution | 0.05 degrees (~5.5 km) - reasonable for a study area the size of an irrigation scheme |
| Temporal resolution | Daily, pentad, or monthly; record starts 1981, near-real-time updates; v3 released 2025 |
| Expected format | GeoTIFF or NetCDF (raster); point extraction needed |
| Preprocessing | Clip to study area, extract time series at occurrence/absence point locations, aggregate to relevant windows (e.g., 30/60/90-day rainfall totals) |
| Limitations | Rainfall only - does not cover temperature, humidity, or wind |

### NASA POWER (temperature, humidity, wind, solar)

| Attribute | Detail |
|---|---|
| Contents | Reanalysis-derived meteorological and solar parameters at point or regional level |
| Why needed | Temperature, humidity, and wind speed are not covered by CHIRPS but are ecologically relevant to bird activity and flock movement |
| Public availability | Yes - free REST API, point or regional query, no auth required |
| Licensing | NASA open data policy - free use, no copyright restriction, attribution requested as courtesy |
| Spatial resolution | 0.5 x 0.625 degrees (~50-55 km) for meteorology - coarse relative to CHIRPS |
| Temporal resolution | Daily (also hourly/monthly/climatology APIs available) |
| Expected format | JSON or CSV via direct API response |
| Preprocessing | Minimal - API returns tabular time series directly per point |
| Limitations | At ~55 km resolution, Ahero and Nyamware will very likely sit in the same grid cell. These variables will carry temporal signal but effectively no spatial discrimination between the two schemes - a material constraint on any "disaggregated by scheme" analysis using these features |

**Alternative under evaluation:** ERA5-Land (Copernicus/ECMWF) - same variable set at ~9 km resolution, a meaningful improvement over NASA POWER for this study area. Access via the Copernicus Climate Data Store API (free, requires registration). Feasibility check pending.

---

## 2.3 Vegetation Data

### MODIS NDVI

| Attribute | Detail |
|---|---|
| Contents | Normalized Difference Vegetation Index - proxy for vegetation greenness/health |
| Why needed | Quelea breeding and flocking closely track green vegetation flush (food/seed availability); a leading driver in the ecological literature |
| Public availability | Yes - free via NASA AppEEARS (point/area extraction tool, no GEE account needed) or Google Earth Engine (requires free account, more powerful for area-wide raster work) |
| Licensing | Public domain (NASA) |
| Spatial resolution | 250 m (MOD13Q1) or 500 m (MOD13A1) - both far finer than needed for two irrigation schemes; good enough to show intra-scheme variation |
| Temporal resolution | 16-day composite |
| Expected format | HDF (native) or GeoTIFF (via AppEEARS/GEE export) |
| Preprocessing | Cloud/quality masking using the accompanying QA band, temporal interpolation across the 16-day gaps, extraction at point locations or as area statistics |
| Limitations | 16-day compositing means NDVI can't be matched to bird records at daily precision - matching must snap to the nearest composite period |

**Assessment:** AppEEARS is the lower-friction path for point-based extraction; GEE becomes more valuable if the study area is widened and area-wide raster analysis is needed.

---

## 2.4 Geospatial / Terrain Data

### SRTM DEM (elevation, slope)

| Attribute | Detail |
|---|---|
| Contents | Digital elevation model |
| Why needed | Terrain may influence roosting site selection and local microclimate |
| Public availability | Yes - free via USGS EarthExplorer, OpenTopography, or GEE |
| Licensing | Public domain |
| Spatial resolution | 30 m (SRTM 1 arc-second) |
| Temporal resolution | Static (2000 acquisition) |
| Expected format | GeoTIFF |
| Preprocessing | Slope/aspect derivation via standard GIS tools (rasterio + richdem, or QGIS) |
| Limitations | None significant for this use case |

### HydroSHEDS (rivers, wetlands, water bodies)

| Attribute | Detail |
|---|---|
| Contents | Hydrographic vector layers - river networks, water body polygons, watershed boundaries |
| Why needed | Distance to water (rivers, wetlands, Lake Victoria) is a plausible roosting/breeding-site predictor, since quelea roost in dense reed beds near water |
| Public availability | Yes - free via hydrosheds.org |
| Licensing | Free for non-commercial and most commercial use with attribution |
| Spatial resolution | Vector, derived from SRTM at 15/30 arc-second base |
| Temporal resolution | Static |
| Expected format | Shapefile / GeoPackage |
| Preprocessing | Distance-to-nearest-feature calculation per occurrence/absence point (geopandas + shapely) |
| Limitations | None significant |

### Land Cover / Administrative Boundaries

| Attribute | Detail |
|---|---|
| Contents | Land cover classification, irrigation scheme/administrative boundaries |
| Why needed | Defines the study area precisely; land cover can distinguish rice paddy from surrounding land use |
| Public availability | Mixed. Global land cover (ESA WorldCover, 10 m) is freely available. Precise Ahero/Nyamware irrigation scheme boundary polygons are not guaranteed to exist in any open global dataset - these are typically held by the National Irrigation Authority (Kenya) or may need to be manually digitized from OpenStreetMap/satellite imagery |
| Licensing | ESA WorldCover: CC-BY; OSM: ODbL |
| Spatial resolution | ESA WorldCover: 10 m |
| Temporal resolution | ESA WorldCover: 2020/2021 snapshot |
| Expected format | GeoTIFF (land cover), Shapefile/GeoJSON (boundaries) |
| Preprocessing | Manual boundary digitization likely required if no authoritative polygon exists |
| Limitations | [UNVERIFIED] - scheme boundary availability needs direct checking; this blocks precise study-area definition |

---

## 2.5 Agricultural Data

| Attribute | Detail |
|---|---|
| Contents | Rice growing season / crop calendar, irrigation block maps |
| Why needed | Would let the model account for crop growth stage, which affects both quelea attraction and the practical relevance of "infestation" |
| Public availability | Weak. FAO's Global Crop Calendar gives generic regional rice season windows, not scheme-specific ones. Scheme-specific data would come from Kenya's National Irrigation Authority or KALRO, not confirmed to be openly published |
| Licensing | Varies; FAO data generally open |
| Spatial resolution | Regional/national generic calendars only, unless local data is obtained |
| Temporal resolution | Seasonal (generic) |
| Expected format | PDF reports or tabular summaries, not machine-readable in most cases |
| Preprocessing | Manual encoding of generic season windows as a derived "growth stage" feature |
| Limitations | Weakest data source category in the project - treat as a stretch feature, not a dependency |

---

# 3. Can These Be Combined Into a Single ML Dataset?

**Yes, structurally.** All sources are either point-extractable or raster-extractable, so a common "point-in-space-and-time" join key (latitude, longitude, date) is achievable across bird occurrence, rainfall, meteorology, vegetation, and terrain layers. This is a standard species distribution modeling (SDM) integration pattern with well-supported tooling (geopandas, rasterio, rasterstats).

**Three caveats must be designed for, not assumed away:**

1. **Resolution mismatch is real, not cosmetic.** CHIRPS (~5.5 km) and NDVI (250-500 m) can plausibly show variation across the study area; NASA POWER (~55 km) almost certainly cannot. This must be documented per-feature in the eventual data dictionary rather than presenting all features as equally spatially informative.
2. **The join is presence-only unless absences are deliberately constructed.** Having all the layers does not by itself solve this; it is a dedicated design task.
3. **Temporal alignment is asymmetric.** Bird records are day-precision, CHIRPS can be daily, NDVI is 16-day-composite, and meteorological/agricultural data is coarser still. Feature engineering must explicitly define matching windows per source (e.g., "30-day antecedent rainfall," "nearest NDVI composite") rather than assume a naive exact-date join.

**Conclusion:** technically feasible, contingent on the occurrence-density result (Section 9, Milestone 2.1). If density in the two-scheme bounding box is too sparse, the integration pipeline described here does not need to change - only the study area does.

---

# 4. Critical Data Gaps

1. **[Highest severity, unverified]** Occurrence record density within Ahero/Nyamware specifically.
2. **No true infestation/crop-damage labels.** Every source above informs occurrence, not crop damage - the target variable should be framed as occurrence/habitat-suitability risk unless a damage-report source is found.
3. **No confirmed authoritative irrigation scheme boundary polygon.**
4. **No reliable scheme-specific agricultural calendar.**
5. **No true absence data unless the eBird EBD request is pursued** - GBIF alone cannot support defensible pseudo-absence sampling without additional design work.

---

# 5. Recommended Alternative / Supplementary Datasets

| Gap | Alternative to investigate |
|---|---|
| Coarse meteorology resolution | ERA5-Land (~9 km, Copernicus CDS) instead of / alongside NASA POWER |
| No damage labels | FAO's Migratory Pests unit and regional Quelea control program bulletins (unstructured, manual extraction, narrative value only) |
| No scheme boundary | OpenStreetMap query for "Ahero Irrigation Scheme" / "Nyamware," cross-checked against satellite basemap; Kenya National Irrigation Authority website/reports |
| Sparse occurrence density (if confirmed) | Widen study area to Kisumu County or the Lake Victoria basin quelea range |
| No true absences | eBird EBD request (parallel track, does not block the GBIF-based feasibility check) |

---

# 6. Proposed Final Dataset Architecture

Pending the outcomes in Section 9, the target structure is a single tabular dataset at point-in-space-and-time granularity:

qualeaguard_master_dataset.csv

Identifiers
- record_id
- source (gbif | ebird | pseudo_absence)
- latitude, longitude
- observation_date

Target
- presence (1/0)                      # binary occurrence framing (recommended)
- risk_class (low/med/high)           # only if evidence supports 3 classes post-EDA

Climate features (CHIRPS)
- rainfall_7d, rainfall_30d, rainfall_90d

Meteorology features (NASA POWER or ERA5-Land)
- temp_mean, temp_max, rh_mean, wind_mean   [flag: low/no spatial variance if NASA POWER retained]

Vegetation features (MODIS NDVI)
- ndvi_nearest_composite, ndvi_anomaly

Terrain / hydrology features (SRTM, HydroSHEDS)
- elevation, slope, dist_to_river, dist_to_wetland, dist_to_water

Temporal features
- month, season, day_of_year

Spatial partition key
- grid_cell_id                          # 5.5km x 5.5km regular grid cell identifier (Log Entry 002)
- within_scheme_boundary (1/0)          # whether the cell falls within the Ahero Irrigation Scheme itself, vs. the surrounding 50km ecological buffer

This schema is provisional and will be finalized once study area, target framing, and pseudo-absence strategy are locked in.

---

# 7. Engineering Decisions

| Decision | Status | Rationale |
|---|---|---|
| Use CHIRPS as the primary rainfall source | Approved | Best available resolution (~5.5 km) for a study area this size, precipitation-focused, long historical record, free and reliably maintained |
| Use MODIS NDVI (via AppEEARS initially) as the primary vegetation source | Approved | Sufficient resolution to capture intra-scheme variation; AppEEARS avoids GEE account setup during the discovery phase |
| Use SRTM DEM and HydroSHEDS for terrain/hydrology | Approved | Mature, stable, high-resolution, no viable open alternative offers meaningful improvement for this use case |
| Frame the target variable as occurrence/habitat-suitability risk rather than "infestation risk" | Approved | GBIF/eBird are presence-based observation data, not crop-damage records; this framing is the scientifically defensible one given available data (see Section 4, item 2) |
| Meteorology source: ERA5-Land selected over NASA POWER | Approved (Log Entry 003) | Both sources piloted directly (Milestone 2.5). ERA5-Land's ~9km resolution provides meaningful spatial variance across the project's ~5.5km grid; NASA POWER's ~55km resolution would reduce most of the ~330-360 grid cells to near-identical values, contributing temporal but not spatial signal. One-time CDS registration/license acceptance completed. |
| Study area scope | Approved (Log Entry 001, Log Entry 002) | Ahero Irrigation Scheme confirmed as sole study area (Log Entry 001); analysis extent defined as Ahero + 50km ecological buffer (Log Entry 002) |
| Pseudo-absence generation strategy | Pending | Depends on whether eBird EBD access is secured; design differs meaningfully between GBIF-only and GBIF+EBD scenarios |
| Irrigation scheme boundary source | Approved (partially superseded) | Ahero Irrigation Scheme boundary confirmed via OpenStreetMap (Milestone 2.1). Individual operational block boundaries confirmed unavailable from any authoritative source and no longer required, since the adopted spatial framework uses a regular grid rather than block-level polygons (Log Entry 002, Section 11) |
| Binary vs. multi-class target | Pending | Requires EDA on the actual occurrence data before deciding; multi-class only if data volume and label confidence support it |
| Spatial (not random) cross-validation for evaluation | Approved | Standard practice for spatially autocorrelated ecological data; prevents inflated performance estimates, directly supports the disaggregated-by-scheme evaluation already committed to in the Specification |

---

# 8. Go / No-Go Criteria

These criteria define when QueleaGuard, as currently scoped, is considered technically feasible versus requiring a scope or methodology revisit. They are evaluated after Milestone 2.1 and re-checked after Milestone 2.2 if the study area changes.

## Go Criteria (proceed as currently scoped)

- At least a modest number of confirmed Quelea quelea occurrence records (exact threshold to be set once density is known, but informally: enough records to support a meaningful train/test split after accounting for spatial clustering - likely in the low hundreds at minimum for a workable binary classifier) exist within the chosen study area.
- Environmental data sources (CHIRPS, NDVI, terrain/hydrology, and a meteorology source) are all confirmed accessible and extractable at the chosen study area's scale.
- A defensible pseudo-absence or true-absence strategy can be designed given the occurrence data's structure.
- Environmental features show non-trivial variance across the study area (i.e., the resolution mismatch in Section 3 does not reduce every feature to a constant).

## No-Go / Revisit Criteria (scope or methodology change required)

- Occurrence records within even a widened bounding box (up to Lake Victoria basin scale) are too sparse to support any reliable train/test split.
- No defensible way to construct absences is found (GBIF-only, no EBD access, no alternative negative-sampling design).
- Environmental features show effectively zero spatial variance across the entire study area at all candidate scales, undermining the geospatial premise of the project.
- [Superseded by Log Entry 002] Disaggregated evaluation is no longer contingent on irrigation scheme boundary data - see Section 11 for the adopted grid-based spatial framework, which performs disaggregated evaluation via spatial cross-validation folds or distance bands instead.

**If a No-Go condition is triggered**, the response is a scope adjustment (wider study area, reframed target variable, or descoped disaggregated evaluation) - not project cancellation. These criteria exist to catch that decision early, at low cost, rather than after feature engineering has begun.

---

# 9. Dataset Status Tracker

| Dataset | Selected | Verified | Downloaded | Integrated |
|---|---|---|---|---|
| GBIF (bird occurrence) | Yes | No | No | No |
| eBird EBD (bird occurrence + effort) | Pending decision | No | No | No |
| CHIRPS (rainfall) | Yes | No | No | No |
| NASA POWER (meteorology) | Not selected (Log Entry 003) | Yes (Milestone 2.5 pilot) | Yes (pilot only) | No |
| ERA5-Land (meteorology) | Yes (Log Entry 003) | Yes (Milestone 2.5 pilot) | Yes (pilot only) | No |
| MODIS NDVI (vegetation) | Yes | No | No | No |
| SRTM DEM (elevation/slope) | Yes | No | No | No |
| HydroSHEDS (hydrology) | Yes | No | No | No |
| ESA WorldCover / OSM (land cover, boundaries) | Yes (pending boundary confirmation) | Yes (pending boundary confirmation) | No | No |
| Agricultural calendar (FAO / NIA / KALRO) | No (stretch feature) | No | No | No |

This table will be updated at the space of each Phase 2 milestone as datasets move through verification, download, and integration.

---

# 10. Status of This Document

This document is finalized for the current phase (Version 1.0). It supersedes the v0.1 draft and is now the authoritative Dataset Feasibility Study for QueleaGuard. It will be revisited and versioned upward as Engineering Decisions move from Pending/Under Review to Approved, and as the Dataset Status Trackerer through Phase 2 execution.

---

> **Project Motto**
>
> *Predict Early. Protect Harvests.*


---

# 11. Spatial Framework (Addendum - Log Entry 002)

This section supersedes prior study-area framing elsewhere in this document wherever it conflicts with the framework below. Full evidence and rationale: docs/assumptions_and_decision_log.md, Log Entry 002.

Following a dedicated literature review and empirical verification (Milestone 2.4), QueleaGuard adopts a regular spatial grid as its permanent spatial framework, replacing any assumption of scheme-level or operational-block-level polygons as the modelling unit:

- **Study area:** Ahero Irrigation Scheme - the real-world system the project aims to support.
- **Analysis extent:** Ahero Irrigation Scheme plus a 50km ecologically justified buffer, supported by three independent lines of evidence: Red-billed Quelea daily foraging range (50-65km reported; conservative lower bound adopted), empirical occurrence coverage (85.1% of confirmed GBIF/eBird records fall within 50km of Ahero), and unrestricted environmental predictor availability at this scale. The wider landscape within this radius - including the Nyando River corridor and its connection to Lake Victoria's Winam Gulf - is treated as a plausible ecological landscape influencing quelea movement, consistent with published knowledge of the species' ecology, not as a confirmed or site-verified roosting area.
- **Spatial unit of analysis:** 5.5km x 5.5km regular grid cells, matching CHIRPS's native resolution, selected as a deliberate methodological decision balancing environmental data resolution, occurrence density, Red-billed Quelea movement ecology, computational efficiency, reproducibility, and SDM literature precedent jointly, rather than any single factor being decisive.
- **Prediction target:** infestation risk predicted per grid cell within the analysis extent, with primary decision-support focus remaining the Ahero Irrigation Scheme itself.

This framework replaces the two-scheme (Ahero/Nyamware) and operational-block polygon framings referenced elsewhere in this document as historical context only; earlier sections are retained for traceability but should be read as superseded where they conflict with this one.

**Relationship to potential dataset publication:** whether the resulting gridded dataset (Section 6 schema) is ever published as an open, citable dataset is governed separately by docs/dataset_publication_strategy.md, which defers that decision pending implementation maturity, licensing review, and scientific evaluation. Nothing in this document should be read as committing to open dataset publication.
