"""
Milestone 2.4 - Spatial Grain Size Selection Analysis

Evaluates candidate grid cell sizes for the QueleaGuard spatial modelling
unit against: literature precedent, native environmental dataset resolution,
occurrence record density, and Red-billed Quelea ecology (movement range,
foraging behavior, water dependency).

This does not select a final grain size automatically - it lays out the
evidence systematically so the decision can be made deliberately and
documented with full justification, per the project's publication-readiness
standard.

Output: reports/milestone_2_4_grain_size_analysis.txt
"""

candidate_cell_sizes_m = [250, 500, 1000, 5000]

native_resolutions = {
    "MODIS NDVI (MOD13Q1)": "250 m",
    "MODIS NDVI (MOD13A1)": "500 m",
    "SRTM DEM": "30 m",
    "CHIRPS rainfall": "~5,500 m (0.05 deg)",
    "NASA POWER meteorology": "~50,000-55,000 m (0.5 x 0.625 deg)",
}

occurrence_context = {
    "Total Kisumu County records (raw, Milestone 2.1)": 161,
    "Records within tight Ahero-area bounding box": 56,
    "Estimated unique space-time events (post-duplicate collapse, approx)": "~110-120 (pending formal dedup)",
}

quelea_ecology_context = {
    "Daily foraging flight distance": "50-65 km reported (multiple independent sources)",
    "Typical distance to water dependency": "~30 km reported",
    "Movement pattern": "Highly mobile, nomadic, daily commuting between roost/feed/water sites",
}

literature_precedent = {
    "Cheke, Venn & Jones (2007)": "Quarter-degree grid squares (~27.75 km at the equator) for quelea breeding-suitability forecasting, southern Africa",
    "Dobson et al. (2023, dynamicSDM)": "Raster-based SDM for Quelea lathamii; pseudo-absence buffers sized to species movement capability and habitat-change rate, not administrative units",
    "General SDM literature (e.g. Moudry et al. resolution studies)": "Grain size explicitly identified as a methodological choice requiring justification; performance and spatial pattern outputs both shown to depend on resolution choice",
}


def main():
    lines = []
    lines.append("Milestone 2.4 - Spatial Grain Size Selection Analysis")
    lines.append("=" * 60)
    lines.append("")

    lines.append("1. NATIVE RESOLUTION OF ENVIRONMENTAL DATASETS")
    lines.append("-" * 60)
    for source, res in native_resolutions.items():
        lines.append(f"  {source}: {res}")
    lines.append("")

    lines.append("2. OCCURRENCE RECORD DENSITY CONTEXT (Milestone 2.1 findings)")
    lines.append("-" * 60)
    for label, val in occurrence_context.items():
        lines.append(f"  {label}: {val}")
    lines.append("")

    lines.append("3. RED-BILLED QUELEA ECOLOGY")
    lines.append("-" * 60)
    for label, val in quelea_ecology_context.items():
        lines.append(f"  {label}: {val}")
    lines.append("")

    lines.append("4. LITERATURE PRECEDENT FOR GRAIN SIZE")
    lines.append("-" * 60)
    for source, note in literature_precedent.items():
        lines.append(f"  {source}: {note}")
    lines.append("")

    lines.append("5. CANDIDATE CELL SIZES UNDER CONSIDERATION")
    lines.append("-" * 60)
    for size in candidate_cell_sizes_m:
        lines.append(f"  {size} m")
    lines.append("")

    lines.append("6. KEY TENSION TO RESOLVE")
    lines.append("-" * 60)
    lines.append(
        "  Fine grain (250-500m, matching MODIS) offers high spatial detail but"
    )
    lines.append(
        "  risks false precision given sparse, presence-only occurrence data"
    )
    lines.append(
        "  (Milestone 2.1: ~56-120 usable points depending on deduplication)."
    )
    lines.append(
        "  Coarse grain (~5.5km, matching CHIRPS) aligns with our lowest-resolution"
    )
    lines.append(
        "  *usable* variable and matches the scale at which Cheke et al. (2007)"
    )
    lines.append(
        "  operated for the same species, but discards spatial detail from MODIS"
    )
    lines.append(
        "  and SRTM. NASA POWER's ~55km resolution is too coarse to inform grain"
    )
    lines.append(
        "  size directly (already flagged in the Dataset Feasibility Study as"
    )
    lines.append(
        "  contributing temporal, not spatial, signal)."
    )
    lines.append("")

    lines.append("This analysis presents evidence only. Final grain size selection")
    lines.append("requires a deliberate decision, to be recorded in the Assumptions")
    lines.append("& Decision Log with full rationale before geospatial implementation")
    lines.append("proceeds.")

    output = "\n".join(lines)
    print(output)

    with open("reports/milestone_2_4_grain_size_analysis.txt", "w") as f:
        f.write(output)
    print("\n\nSaved to reports/milestone_2_4_grain_size_analysis.txt")


if __name__ == "__main__":
    main()
