import csv
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

# 1. Identities
with open(os.path.join(DATASET_DIR, "user_identities.csv"), "r", encoding="utf-8") as f:
    users_by_email = {r["email"].lower(): r for r in csv.DictReader(f)}
    f.seek(0)
    users_by_id = {r["user_id"]: r for r in csv.DictReader(f)}

with open(os.path.join(DATASET_DIR, "user_audit_log.csv"), "r", encoding="utf-8") as f:
    audit_logs = list(csv.DictReader(f))

hist_emails = {}
all_user_emails = {}
all_user_hashes = {}
for u, r in users_by_id.items():
    all_user_emails[u] = {r["email"].lower()}
    all_user_hashes[u] = {r["email_hash"].lower()} if r["email_hash"] else set()

for a in audit_logs:
    u = a["user_id"]
    if a["field_name"] == "email":
        hist_emails[a["old_value"].lower()] = u
        hist_emails[a["new_value"].lower()] = u
        all_user_emails[u].add(a["old_value"].lower())
        all_user_emails[u].add(a["new_value"].lower())
    elif a["field_name"] == "email_hash":
        all_user_hashes[u].add(a["old_value"].lower())
        all_user_hashes[u].add(a["new_value"].lower())

with open(os.path.join(DATASET_DIR, "deletion_requests.csv"), "r", encoding="utf-8") as f:
    eval_requests = list(csv.DictReader(f))

print(f"Total eval requests: {len(eval_requests)}")

# 2. Check activities around reported_at
with open(os.path.join(DATASET_DIR, "system_activity.csv"), "r", encoding="utf-8") as f:
    activities = list(csv.DictReader(f))

# Index activities by time
activities_sorted = sorted(activities, key=lambda x: x["event_time"])

matched_accounts = 0
unmatched_accounts = []

for req in eval_requests:
    cid = req["case_id"]
    email = req["email"].lower()
    uid = users_by_email.get(email, {}).get("user_id") or hist_emails.get(email)
    rep_at = req["reported_at"]
    req_at = req["requested_at"]
    
    # Check if there's an activity for account_service around reported_at
    # Look for activities within 2 hours of reported_at
    found = False
    for a in activities:
        if a["target_system"] == "account_service" and a["event_type"] == "DELETE_RECORD":
            # check if details or resource matches or time matches
            # Let's see if time is close to reported_at
            t = a["event_time"]
            if abs((abs(int(t[11:13])*60 + int(t[14:16])) - (int(rep_at[11:13])*60 + int(rep_at[14:16])))) < 120 and t[:10] == rep_at[:10]:
                found = True
                break
    if found:
        matched_accounts += 1
    else:
        unmatched_accounts.append(cid)

print(f"Matched account activities by time: {matched_accounts}/{len(eval_requests)}")
