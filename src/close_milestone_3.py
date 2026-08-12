"""
Milestone 3 closure - Update Dataset Status Tracker to reflect full
integration of all core sources into the final modelling dataset, and
append a closing statement marking Milestone 3 (Data Engineering) complete.
"""

path = "docs/dataset_feasibility_study.md"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

replacements = {
    "| GBIF (bird occurrence) | Yes | No | No | No |":
        "| GBIF (bird occurrence) | Yes | Yes | Yes | Yes |",
    "| CHIRPS (rainfall) | Yes | No | No | No |":
        "| CHIRPS (rainfall) | Yes | Yes | Yes | Yes |",
    "| ERA5-Land (meteorology) | Yes (Log Entry 003) | Yes (Milestone 2.5 pilot) | Yes (pilot only) | No |":
        "| ERA5-Land (meteorology) | Yes (Log Entry 003) | Yes | Yes | Yes |",
    "| MODIS NDVI (vegetation) | Yes | Yes (Milestone 2.6 AppEEARS pilot) | Yes (pilot only) | No |":
        "| MODIS NDVI (vegetation) | Yes | Yes | Yes | Yes (corrected, Log Entry 012) |",
    "| SRTM DEM (elevation/slope) | Yes | No | No | No |":
        "| SRTM DEM (elevation/slope) | Yes | Yes | Yes | Yes |",
    "| HydroSHEDS (hydrology) | Yes | No | No | No |":
        "| HydroSHEDS (hydrology) | Yes | Yes | Yes | Yes |",
}

for old, new in replacements.items():
    if old not in content:
        print(f"WARNING: expected text not found, skipped:\n  {old}")
    else:
        content = content.replace(old, new)
        print(f"Updated: {old.split('|')[1].strip()}")

closure_note = """

---

# 13. Milestone 3 Closure Statement

Milestone 3 (Data Engineering) is complete as of 2026-08-12. Summary of outcomes:

- **Spatial framework:** 328-cell, 5.5km analysis grid generated over the 50km-buffered Ahero extent (Milestone 3.1, Log Entry 002). 4 cells fall within the scheme boundary itself.
- **Occurrence-to-grid join:** 145 of 161 raw GBIF records matched to the grid (Milestone 3.2); 133 retained as feature-complete modelling candidates after the MODIS temporal boundary filter (Milestone 3.3, Log Entry 006).
- **Pseudo-absence generation:** Approximate Target-Group Background sampling implemented (Milestone 3.9, Log Entry 009), 133 initial records, scheme-boundary coverage gap investigated and accepted (Log Entry 010), month-only date precision resolved (Log Entry 011).
- **Environmental feature extraction:** Rainfall (CHIRPS), meteorology (ERA5-Land), NDVI (MODIS via AppEEARS), terrain (SRTM), and hydrology (HydroSHEDS) all extracted for both presence and pseudo-absence record sets, with zero missing values in the final dataset.
- **Data integrity corrections (Milestone 3.10-3.11):** A quality-filter bug in NDVI extraction (MODIS fill value -3000 selected as valid NDVI in 8 records) was identified and fixed at the extraction-script level, not patched downstream (Log Entry 012). This surfaced 4 pseudo-absence records that pre-date MODIS's first valid composite, excluded per the existing Log Entry 006 precedent. Full dataset validation then identified and corrected a genuine Target-Group Background assumption violation: 3 pseudo-absence records shared a checklist/date/cell with a confirmed presence record and were excluded (Log Entry 013).
- **Final validated dataset:** 259 records (133 presence, 126 pseudo-absence), 20 columns, zero missing values, all features within physically plausible ranges, zero duplicate record keys, zero presence/pseudo-absence class contradictions. Remaining same-(cell,date) duplicates (164 of 259) are explained and legitimate: independent multi-observer records of persistent sites (presence side, consistent with the cell_0080 finding in Log Entry 004) and multi-species same-checklist records (pseudo-absence side, confirmed via direct species cross-check).

**Known, accepted limitations carried into Phase 4:**
- Class balance is 133:126, not the originally planned exact 1:1 (Log Entry 009), due to the two exclusion rounds above. Negligible for the planned tree-based models.
- Zero pseudo-absences fall within the 4 scheme-boundary grid cells (Log Entry 010) - accepted, with environmental-representativeness support for model interpolation.
- Temporal features (month, season, day_of_year) from the original schema sketch (Dataset Feasibility Study, Section 6) are not yet present in the final dataset - flagged for Phase 5 (Feature Engineering finalization), not a Phase 3 blocker.

The dataset is frozen as the modelling-ready foundation for Phase 4 (Exploratory Data Analysis).
"""

content = content + closure_note

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("\nMilestone 3 closure statement appended.")
