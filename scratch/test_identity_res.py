import csv
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

# 1. Load user identities
with open(os.path.join(DATASET_DIR, "user_identities.csv"), "r", encoding="utf-8") as f:
    identities_rows = list(csv.DictReader(f))

# 2. Load audit log
with open(os.path.join(DATASET_DIR, "user_audit_log.csv"), "r", encoding="utf-8") as f:
    audit_rows = list(csv.DictReader(f))

# Build identity maps
current_by_email = {r["email"].lower(): r for r in identities_rows}
current_by_id = {r["user_id"]: r for r in identities_rows}

historical_emails_to_user = {}
for a in audit_rows:
    if a["field_name"] == "email":
        historical_emails_to_user[a["old_value"].lower()] = a["user_id"]
        historical_emails_to_user[a["new_value"].lower()] = a["user_id"]

def resolve_user(email):
    e = email.strip().lower()
    if e in current_by_email:
        return current_by_email[e]["user_id"], "current"
    if e in historical_emails_to_user:
        return historical_emails_to_user[e], "historical"
    return None, "unresolved"

# Test on 32 samples
with open(os.path.join(DATASET_DIR, "sample_deletion_requests.csv"), "r", encoding="utf-8") as f:
    sample_requests = list(csv.DictReader(f))

sample_unresolved = []
for r in sample_requests:
    uid, method = resolve_user(r["email"])
    if not uid:
        sample_unresolved.append(r)
print(f"Sample requests: {len(sample_requests)}, unresolved: {len(sample_unresolved)}")

# Test on 518 deletion requests
with open(os.path.join(DATASET_DIR, "deletion_requests.csv"), "r", encoding="utf-8") as f:
    del_requests = list(csv.DictReader(f))

del_unresolved = []
hist_count = 0
for r in del_requests:
    uid, method = resolve_user(r["email"])
    if not uid:
        del_unresolved.append(r)
    elif method == "historical":
        hist_count += 1

print(f"Full requests: {len(del_requests)}, unresolved: {len(del_unresolved)}, resolved via historical email: {hist_count}")
if del_unresolved:
    for r in del_unresolved:
        print(f"  Unresolved: {r['case_id']} | {r['email']}")
