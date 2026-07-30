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
