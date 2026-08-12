"""
Update Implementation Roadmap checkboxes to reflect actual Milestone 3
completion state (previously stale per the roadmap audit).
"""

path = "docs/implementation_roadmap.md"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

replacements = {
    "- [ ] Dataset collected": "- [x] Dataset collected",
    "- [ ] Dataset cleaned": "- [x] Dataset cleaned",
}

for old, new in replacements.items():
    if old not in content:
        print(f"WARNING: not found, skipped: {old}")
    else:
        content = content.replace(old, new)
        print(f"Updated: {old}")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("\nRoadmap checkboxes updated. Data dictionary checkbox left unchecked - not yet created.")
