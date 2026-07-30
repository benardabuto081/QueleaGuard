"""
Milestone 2.4 (continued) - Apply targeted corrections to Data & Methodology
to reflect the spatial framework decision (Log Entry 002).
"""

path = "docs/data_and_methodology.md"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

replacements = [
    (
        """# 5. Study Area

The project focuses on:

- **Ahero Irrigation Scheme** - a single, NIA-administered, gazetted (4,176 acres) rice irrigation scheme established in 1966, in the Kano Plains near the lower basin of the Nyando River.
- Named sub-blocks within the scheme, including Ahero, Okana, Mbega, Kasiru/Kolal, Nokiso, Masune, and Kobong'o, used as the disaggregated evaluation unit (see Section 12).
- The surrounding rice-growing communities adjacent to the scheme, including Nyamware village.

Kisumu County, Kenya

This localized approach enables the model to capture environmental patterns specific to one of Kenya's most important rice-growing regions.""",
        """# 5. Study Area, Analysis Extent, and Spatial Unit of Analysis

Following a dedicated spatial framework decision (see docs/assumptions_and_decision_log.md, Log Entry 002), the project distinguishes:

- **Study area:** **Ahero Irrigation Scheme** - a single, NIA-administered, gazetted (4,176 acres) rice irrigation scheme established in 1966, in the Kano Plains near the lower basin of the Nyando River, comprising named operational blocks including Ahero, Okana, Mbega, Kasiru/Kolal, Nokiso, Masune, Kobong'o, South West Kano, and Ayweyo.
- **Analysis extent:** the Ahero Irrigation Scheme plus a 50km ecologically justified buffer, grounded in Red-billed Quelea daily foraging range (50-65km reported, conservative lower bound adopted), empirical occurrence coverage (85.1% of confirmed GBIF/eBird records fall within 50km of Ahero), and unrestricted environmental predictor availability at this scale. The surrounding rice-growing communities, including Nyamware village, fall within this extent as ecological/modelling context.
- **Spatial unit of analysis:** 5.5km x 5.5km regular grid cells (matching CHIRPS's native resolution), used for disaggregated evaluation (see Section 12) in place of the named operational blocks, since no authoritative GIS boundaries exist for the individual blocks.

Kisumu County, Kenya

This localized approach enables the model to capture environmental patterns specific to one of Kenya's most important rice-growing regions, following established species distribution modelling (SDM) practice for grid-based spatial units.""",
    ),
    (
        "- Disaggregated Evaluation by irrigation scheme sub-block (Ahero, Okana, Mbega, Kasiru/Kolal, Nokiso, Masune, Kobong'o), if feasible - replacing the originally planned two-scheme disaggregation (see docs/assumptions_and_decision_log.md, Log Entry 001)",
        "- Disaggregated Evaluation by spatial partition (spatial cross-validation fold or distance-from-scheme-center band), if feasible - superseding the sub-block disaggregation approach considered after the Nyamware correction (docs/assumptions_and_decision_log.md, Log Entry 001), following the grid-based spatial framework adopted in Log Entry 002",
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

print("\nData & Methodology updated and saved.")
