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
