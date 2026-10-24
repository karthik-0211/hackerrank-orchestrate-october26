import csv
import json
import os

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

with open(os.path.join(DATASET_DIR, "system_activity.csv"), "r", encoding="utf-8") as f:
    activities = list(csv.DictReader(f))

matches = [a for a in activities if "account_004" in json.dumps(a)]
print(f"Matches for account_004: {len(matches)}")
for m in matches:
    print(m)
