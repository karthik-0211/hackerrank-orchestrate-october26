import csv
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

# Load sample requests and sample outputs
with open(os.path.join(DATASET_DIR, "sample_deletion_requests.csv"), "r", encoding="utf-8") as f:
    sample_requests = {r["case_id"]: r for r in csv.DictReader(f)}

with open(os.path.join(DATASET_DIR, "sample_output.csv"), "r", encoding="utf-8") as f:
    sample_outputs = {r["case_id"]: r for r in csv.DictReader(f)}

# Load user identities
with open(os.path.join(DATASET_DIR, "user_identities.csv"), "r", encoding="utf-8") as f:
    identities = {r["email"].lower(): r for r in csv.DictReader(f)}
    # Also index by user_id
    f.seek(0)
    users_by_id = {r["user_id"]: r for r in csv.DictReader(f)}

# Load user audit log
with open(os.path.join(DATASET_DIR, "user_audit_log.csv"), "r", encoding="utf-8") as f:
    audit_logs = list(csv.DictReader(f))

# Map old email to user_id
historical_emails = {}
for a in audit_logs:
    if a["field_name"] == "email":
        historical_emails[a["old_value"].lower()] = a["user_id"]
        historical_emails[a["new_value"].lower()] = a["user_id"]

print(f"Loaded {len(identities)} user identities, {len(audit_logs)} audit logs, {len(historical_emails)} email audit mappings.")

# Let's test resolving each sample case email
for case_id, req in sample_requests.items():
    email = req["email"].lower()
    user_id = None
    if email in identities:
        user_id = identities[email]["user_id"]
    elif email in historical_emails:
        user_id = historical_emails[email]
    
    expected_status = sample_outputs[case_id]["deletion_status"]
    expected_steps = json.loads(sample_outputs[case_id]["steps_json"])
    print(f"[{case_id}] req_email={email} -> user_id={user_id} expected_status={expected_status} ({len(expected_steps)} steps)")
    for step in expected_steps:
        print(f"    {step['phase']} | {step['system_id']} | {step['resource_id']} | {step['operation']} | {step['state']} | ev={step['evidence_id']}")
