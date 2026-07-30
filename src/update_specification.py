"""
Milestone 2.4 (continued) - Apply targeted corrections to the Project
Specification to reflect the spatial framework decision (Log Entry 002).
"""

path = "docs/project_specification.md"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

replacements = [
    (
        """# 5. Study Area

The study focuses on:

- **Ahero Irrigation Scheme** - a single, NIA-administered, gazetted (4,176 acres) rice irrigation scheme established in 1966, comprising named sub-blocks including Ahero, Okana, Mbega, Kasiru/Kolal, Nokiso, Masune, and Kobong'o.
- The surrounding rice-growing communities adjacent to the scheme, including Nyamware village, acknowledged as part of the broader agricultural and ecological context.

Location:

Kisumu County, Kenya

This localized scope allows the project to address a real agricultural challenge while maintaining a manageable dataset and implementation timeline.""",
        """# 5. Study Area, Analysis Extent, and Spatial Unit of Analysis

Following a dedicated spatial framework decision (see docs/assumptions_and_decision_log.md, Log Entry 002), the project distinguishes three related but distinct concepts:

- **Study area:** **Ahero Irrigation Scheme** - a single, NIA-administered, gazetted (4,176 acres) rice irrigation scheme established in 1966, comprising named operational blocks including Ahero, Okana, Mbega, Kasiru/Kolal, Nokiso, Masune, Kobong'o, South West Kano, and Ayweyo. This is the real-world system the project aims to support, and the primary decision-support focus of the eventual model.
- **Analysis extent:** the Ahero Irrigation Scheme plus a 50km ecologically justified buffer, supported by Red-billed Quelea movement ecology (50-65km daily foraging range), empirical occurrence coverage (85.1% of confirmed records fall within 50km of Ahero), and unrestricted environmental predictor availability at this scale. The surrounding rice-growing communities, including Nyamware village, and the wider landscape within this radius fall within the analysis extent as ecological/modelling context.
- **Spatial unit of analysis:** 5.5km x 5.5km regular grid cells (matching CHIRPS's native resolution), not administrative or operational-block polygons. This was adopted following a literature review of species distribution modelling (SDM) practice, which consistently uses grid/raster-based spatial units, combined with confirmation that no authoritative GIS boundaries exist for individual operational blocks.

Location:

Kisumu County, Kenya

This localized approach allows the project to address a real agricultural challenge while maintaining a manageable dataset and implementation timeline, and follows established SDM methodology rather than relying on administrative boundaries.""",
    ),
    (
        '**Additional Requirement:**\nThe project will also include **disaggregated evaluation by irrigation scheme sub-block** (e.g., Ahero, Okana, Mbega, Kasiru/Kolal, Nokiso, Masune, Kobong\'o) if the dataset supports meaningful subgroup analysis. This replaces the originally planned two-scheme disaggregation following the Nyamware correction (see docs/assumptions_and_decision_log.md, Log Entry 001) and is a more accurate design, since these sub-blocks are real administratively-distinct units within the single confirmed scheme.',
        '**Additional Requirement:**\nThe project will also include **disaggregated evaluation by spatial partition** (e.g., spatial cross-validation fold or distance-from-scheme-center band) if the dataset supports meaningful subgroup analysis. This supersedes the block-level disaggregation approach considered after the Nyamware correction (docs/assumptions_and_decision_log.md, Log Entry 001), following the adoption of a grid-based spatial framework in Log Entry 002 - operational block boundaries are not available from any authoritative source, whereas spatial partitions within the grid require no such data and are standard SDM evaluation practice.',
    ),
]

for old, new in replacements:
    if old not in content:
        print(f"WARNING: expected text not found, skipped (first 80 chars):\n  {old[:80]}...")
    else:
        content = content.replace(old, new)
        print(f"Applied replacement (first 60 chars): {old[:60]}...")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("\nProject Specification updated and saved.")
