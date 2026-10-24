import csv
import os
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

with open(os.path.join(DATASET_DIR, "system_activity.csv"), "r", encoding="utf-8") as f:
    activities = list(csv.DictReader(f))

print(f"Total system activities: {len(activities)}")

event_types = Counter(a["event_type"] for a in activities)
print("\nEvent types in system_activity:")
for et, c in event_types.most_common():
    print(f"  {et}: {c}")

sources = Counter(a["source_system"] for a in activities)
print("\nSource systems:")
for s, c in sources.most_common():
    print(f"  {s}: {c}")

targets = Counter(a["target_system"] for a in activities)
print("\nTarget systems:")
for t, c in targets.most_common():
    print(f"  {t}: {c}")

results = Counter(a["reported_result"] for a in activities)
print("\nReported results:")
for res, c in results.most_common():
    print(f"  {res}: {c}")
