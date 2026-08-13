"""
Deeper diagnosis: the eventDate values LOOK like valid ISO dates on visual
inspection but pd.to_datetime is failing on 118/133. Check for hidden
characters, duplicate column names, or dtype issues before assuming
anything about the data itself.
"""

import pandas as pd

print("=== Raw CSV header ===")
with open("data/processed/pseudo_absences_final.csv", "r", encoding="utf-8") as f:
    print(f.readline())

sampled = pd.read_csv("data/processed/pseudo_absences_final.csv")
print("\n=== Actual column names (repr) ===")
print([repr(c) for c in sampled.columns])

print("\n=== dtype of eventDate column ===")
print(sampled["eventDate"].dtype)

print("\n=== First 5 raw values with repr() to catch hidden characters ===")
for v in sampled["eventDate"].head(5):
    print(repr(v))

print("\n=== Try parsing first 5 values individually ===")
for v in sampled["eventDate"].head(5):
    try:
        result = pd.to_datetime(v)
        print(f"{repr(v)} -> {result}")
    except Exception as e:
        print(f"{repr(v)} -> FAILED: {e}")

print("\n=== Column count check (any duplicate 'eventDate' columns?) ===")
print(sampled.columns.tolist())
