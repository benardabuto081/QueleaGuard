with open("docs/project_charter.md", "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace("- Bernard Abuto\n- Faith Kipruto\n", "- Bernard Abuto\n")
with open("docs/project_charter.md", "w", encoding="utf-8") as f:
    f.write(content)
print("project_charter.md updated")

with open("docs/implementation_roadmap.md", "r", encoding="utf-8") as f:
    content = f.read()
old = """## Faith Kipruto

Primary Responsibilities

- Literature review
- Data validation
- Exploratory data analysis
- Model evaluation
- Responsible AI documentation
- Presentation preparation

---

"""
content = content.replace(old, "")
with open("docs/implementation_roadmap.md", "w", encoding="utf-8") as f:
    f.write(content)
print("implementation_roadmap.md updated")
