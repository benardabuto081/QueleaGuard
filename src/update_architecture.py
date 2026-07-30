"""
Milestone 2.4 (continued) - Apply targeted correction to Technical
Architecture to reflect the spatial framework decision (Log Entry 002).
"""

path = "docs/technical_architecture.md"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = "- Disaggregated evaluation by irrigation scheme sub-block (Ahero, Okana, Mbega, Kasiru/Kolal, Nokiso, Masune, Kobong'o), where applicable"
new = "- Disaggregated evaluation by spatial partition (spatial cross-validation fold or distance-from-scheme-center band), per the grid-based spatial framework adopted in docs/assumptions_and_decision_log.md, Log Entry 002 - superseding block-level disaggregation, since operational block boundaries are not available from any authoritative source"

if old not in content:
    print("WARNING: expected text not found, skipped.")
else:
    content = content.replace(old, new)
    print("Applied replacement to Section 9 (Model Evaluation Layer).")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Technical Architecture updated and saved.")
