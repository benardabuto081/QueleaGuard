"""
Milestone 2.5 (continued) - Apply targeted correction to Dataset
Feasibility Study reflecting the ERA5-Land meteorology decision (Log Entry 003).
"""

path = "docs/dataset_feasibility_study.md"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

replacements = [
    (
        "| Meteorology source: NASA POWER vs. ERA5-Land | Under Review | NASA POWER is lower-friction (no registration) but ~55 km resolution likely erases spatial variance between the two schemes; ERA5-Land offers ~9 km resolution at the cost of CDS registration. Requires a short access-and-resolution comparison before final selection |",
        "| Meteorology source: ERA5-Land selected over NASA POWER | Approved (Log Entry 003) | Both sources piloted directly (Milestone 2.5). ERA5-Land's ~9km resolution provides meaningful spatial variance across the project's ~5.5km grid; NASA POWER's ~55km resolution would reduce most of the ~330-360 grid cells to near-identical values, contributing temporal but not spatial signal. One-time CDS registration/license acceptance completed. |",
    ),
    (
        "| NASA POWER (meteorology) | ⬜ (under review vs. ERA5-Land) | ⬜ | ⬜ | ⬜ |\n| ERA5-Land (meteorology, alternative) | ⬜ (under review) | ⬜ | ⬜ | ⬜ |",
        "| NASA POWER (meteorology) | Not selected (Log Entry 003) | Yes (Milestone 2.5 pilot) | Yes (pilot only) | No |\n| ERA5-Land (meteorology) | Yes (Log Entry 003) | Yes (Milestone 2.5 pilot) | Yes (pilot only) | No |",
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

print("\nDataset Feasibility Study updated with meteorology decision.")
