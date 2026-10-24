import csv
import hashlib
import os

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

with open(os.path.join(DATASET_DIR, "user_audit_log.csv"), "r", encoding="utf-8") as f:
    logs = [r for r in csv.DictReader(f) if r["user_id"] == "user_12"]

for l in logs:
    print(l)
    if l["field_name"] == "email":
        old_h = hashlib.sha256(l["old_value"].lower().encode("utf-8")).hexdigest()
        new_h = hashlib.sha256(l["new_value"].lower().encode("utf-8")).hexdigest()
        print(f"  old_email={l['old_value']} hash={old_h}")
        print(f"  new_email={l['new_value']} hash={new_h}")
