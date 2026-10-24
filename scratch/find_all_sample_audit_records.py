import csv
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

with open(os.path.join(DATASET_DIR, "sample_deletion_requests.csv"), "r", encoding="utf-8") as f:
    sample_requests = {r["case_id"]: r for r in csv.DictReader(f)}

with open(os.path.join(DATASET_DIR, "sample_output.csv"), "r", encoding="utf-8") as f:
    sample_outputs = {r["case_id"]: r for r in csv.DictReader(f)}

# Find audit_record for each case in sample_output
audit_records = {}
for case_id, row in sample_outputs.items():
    steps = json.loads(row["steps_json"])
    for s in steps:
        if s["system_id"] == "security_service":
            audit_records[case_id] = s["resource_id"]

print("Audit records in sample cases:")
for case_id, rec in audit_records.items():
    print(f"  {case_id}: {rec}")
