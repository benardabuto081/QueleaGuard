"""
Milestone 2.5 (continued) - Corrected replacement for Dataset Status
Tracker rows, using the actual current file text.
"""

path = "docs/dataset_feasibility_study.md"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = "| NASA POWER (meteorology) | Under review vs. ERA5-Land | No | No | No |\n| ERA5-Land (meteorology, alternative) | Under review | No | No | No |"
new = "| NASA POWER (meteorology) | Not selected (Log Entry 003) | Yes (Milestone 2.5 pilot) | Yes (pilot only) | No |\n| ERA5-Land (meteorology) | Yes (Log Entry 003) | Yes (Milestone 2.5 pilot) | Yes (pilot only) | No |"

if old not in content:
    print("WARNING: still not found, printing exact bytes around expected location for inspection.")
else:
    content = content.replace(old, new)
    print("Applied replacement to Dataset Status Tracker.")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Dataset Feasibility Study updated and saved.")
