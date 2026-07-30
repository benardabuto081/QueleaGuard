"""
Milestone 2.4 (continued) - Apply targeted corrections to the Dataset
Feasibility Study to reflect the spatial framework decision (Log Entry 002),
without a full document rewrite, per the project owner's instruction.

Corrections:
1. Section 6 dataset schema: replace irrigation_scheme (ahero|nyamware)
   partition key with grid_cell_id / within_scheme_boundary.
2. Section 8 Go/No-Go: replace the scheme-boundary-dependent disaggregation
   criterion with a reference to the grid-based approach.
3. Section 7 Engineering Decisions: update two rows superseded by Log
   Entry 001 and Log Entry 002.
4. Append new Section 11 documenting the spatial framework, referencing
   both the Decision Log and the Dataset Publication Strategy document.

Each replacement is checked before being applied; if an expected string
is not found, the script reports it instead of silently doing nothing.
"""

path = "docs/dataset_feasibility_study.md"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

replacements = [
    (
        "Spatial partition key\n- irrigation_scheme (ahero | nyamware)   # for disaggregated evaluation, spatial CV folds",
        "Spatial partition key\n- grid_cell_id                          # 5.5km x 5.5km regular grid cell identifier (Log Entry 002)\n- within_scheme_boundary (1/0)          # whether the cell falls within the Ahero Irrigation Scheme itself, vs. the surrounding 50km ecological buffer",
    ),
    (
        '- No irrigation scheme boundary or reasonable proxy can be established, preventing meaningful "disaggregated by scheme" evaluation - in this case, the disaggregated evaluation requirement would be descoped rather than the whole project.',
        "- [Superseded by Log Entry 002] Disaggregated evaluation is no longer contingent on irrigation scheme boundary data - see Section 11 for the adopted grid-based spatial framework, which performs disaggregated evaluation via spatial cross-validation folds or distance bands instead.",
    ),
    (
        "| Study area scope (two schemes vs. county vs. basin-wide) | Pending | Depends entirely on Milestone 2.1 occurrence-density results |",
        "| Study area scope | Approved (Log Entry 001, Log Entry 002) | Ahero Irrigation Scheme confirmed as sole study area (Log Entry 001); analysis extent defined as Ahero + 50km ecological buffer (Log Entry 002) |",
    ),
    (
        "| Irrigation scheme boundary source | Pending | No authoritative open polygon confirmed yet; may require manual digitization |",
        "| Irrigation scheme boundary source | Approved (partially superseded) | Ahero Irrigation Scheme boundary confirmed via OpenStreetMap (Milestone 2.1). Individual operational block boundaries confirmed unavailable from any authoritative source and no longer required, since the adopted spatial framework uses a regular grid rather than block-level polygons (Log Entry 002, Section 11) |",
    ),
]

for old, new in replacements:
    if old not in content:
        print(f"WARNING: expected text not found, skipped:\n  {old[:80]}...")
    else:
        content = content.replace(old, new)
        print(f"Applied replacement: {old[:60]}...")

new_section = """

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
"""

content = content + new_section

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("\nDataset Feasibility Study updated and saved.")
