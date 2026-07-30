"""
Milestone 2.4 (continued) - Apply targeted correction to Implementation
Roadmap, noting that Milestone 3 (Data Engineering) now proceeds under the
confirmed spatial framework (Log Entry 002).
"""

path = "docs/implementation_roadmap.md"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = """## Milestone 3 - Data Engineering

Objectives

Construct a machine-learning-ready dataset.

Tasks

- Clean datasets
- Remove duplicates
- Handle missing values
- Standardize coordinate systems
- Merge datasets
- Validate joins
- Export processed dataset

Deliverables

- Processed dataset
- Data dictionary
- Data validation report"""

new = """## Milestone 3 - Data Engineering

Objectives

Construct a machine-learning-ready dataset, using the confirmed spatial framework: a 5.5km x 5.5km regular grid as the unit of analysis, covering the Ahero Irrigation Scheme plus a 50km ecological buffer (see docs/assumptions_and_decision_log.md, Log Entry 002).

Tasks

- Clean datasets
- Remove duplicates
- Handle missing values
- Standardize coordinate systems
- Generate the regular spatial grid across the confirmed analysis extent
- Merge datasets onto the grid (aggregate finer-resolution layers, e.g. MODIS NDVI and SRTM, into grid cells; assign CHIRPS values natively)
- Validate joins
- Export processed dataset

Deliverables

- Processed dataset
- Data dictionary
- Data validation report"""

if old not in content:
    print("WARNING: expected text not found, skipped.")
else:
    content = content.replace(old, new)
    print("Applied replacement to Milestone 3 (Data Engineering).")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Implementation Roadmap updated and saved.")
