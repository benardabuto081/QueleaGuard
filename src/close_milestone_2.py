"""
Milestone 2 closure - Update Dataset Status Tracker for MODIS NDVI, and
append a closing statement marking Milestone 2 (Data Acquisition) complete.
"""

path = "docs/dataset_feasibility_study.md"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = "| MODIS NDVI (vegetation) | Yes | No | No | No |"
new = "| MODIS NDVI (vegetation) | Yes | Yes (Milestone 2.6 AppEEARS pilot) | Yes (pilot only) | No |"

if old not in content:
    print("WARNING: expected text not found, skipped.")
else:
    content = content.replace(old, new)
    print("Applied replacement to MODIS NDVI status row.")

closure_note = """

---

# 12. Milestone 2 Closure Statement

Milestone 2 (Data Acquisition) is complete as of 2026-08-01. Summary of outcomes:

- **Bird occurrence (GBIF):** Feasibility confirmed (Milestone 2.1). Study area corrected from an assumed two-scheme framing to the single confirmed Ahero Irrigation Scheme (Log Entry 001). 161 raw records retrieved for Kisumu County; 85.1% fall within the adopted 50km analysis extent (Log Entry 002).
- **Spatial framework:** Established and documented (Milestone 2.4, Log Entry 002) - study area, analysis extent, and 5.5km grid-based spatial unit of analysis, backed by literature precedent, empirical occurrence distribution, and environmental data availability.
- **Rainfall (CHIRPS):** Access confirmed via direct raster download (Milestone 2.3). Real rainfall value extracted and verified for Ahero.
- **Meteorology (ERA5-Land vs. NASA POWER):** Both piloted; ERA5-Land selected for its ~9km resolution advantage over NASA POWER's ~55km (Milestone 2.5, Log Entry 003).
- **Vegetation (MODIS NDVI):** Access confirmed via NASA AppEEARS (Milestone 2.6). Real NDVI values retrieved with QA/quality fields intact and verified.
- **Terrain/hydrology (SRTM, HydroSHEDS):** Not yet directly piloted with a live data pull; treated as low-risk given their maturity, stability, and lack of viable alternatives noted throughout this document. To be confirmed during Milestone 3 implementation rather than as a separate Milestone 2 pilot, since no access-method uncertainty comparable to the other sources has been identified.
- **Agricultural calendar data:** Remains a stretch feature, unchanged from original assessment (Section 2.5) - weakest data source category, not a Milestone 2 blocker.

**Feature inventory frozen entering Milestone 3:** GBIF/eBird occurrence, CHIRPS rainfall, ERA5-Land meteorology, MODIS NDVI, SRTM elevation/slope, HydroSHEDS hydrology distance features - all confirmed accessible at the resolutions documented in Section 2, gridded onto the 5.5km spatial framework established in Log Entry 002.

Milestone 3 (Data Engineering) may now proceed under a stable, evidence-backed data and spatial foundation.
"""

content = content + closure_note

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Milestone 2 closure statement appended.")
