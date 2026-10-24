import csv
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

with open(os.path.join(DATASET_DIR, "deletion_requests.csv"), "r", encoding="utf-8") as f:
    all_requests = list(csv.DictReader(f))

for r in all_requests:
    num = int(r["case_id"].split("_")[1])
    if num >= 520:
        print(f"[{r['case_id']}] ({r['reported_status']}) {r['request_text']}")
