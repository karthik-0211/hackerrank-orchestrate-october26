import csv
import json
import os
import glob
from collections import defaultdict, Counter

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

with open(os.path.join(DATASET_DIR, "deletion_requests.csv"), "r", encoding="utf-8") as f:
    all_requests = list(csv.DictReader(f))

print(f"Total requests in deletion_requests.csv: {len(all_requests)}")

# Check reported_status distribution
rep_status = Counter(r["reported_status"] for r in all_requests)
print(f"Reported status distribution: {rep_status}")

# Let's inspect some request_text samples
print("\nFirst 10 request texts:")
for i, r in enumerate(all_requests[:10]):
    print(f"Case {r['case_id']}: {r['request_text']}")
