import csv
import json
import os
import sys
from collections import defaultdict
from pypdf import PdfReader

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

# Load requests and identities
with open(os.path.join(DATASET_DIR, "user_identities.csv"), "r", encoding="utf-8") as f:
    identities = {r["email"].lower(): r for r in csv.DictReader(f)}
    f.seek(0)
    users_by_id = {r["user_id"]: r for r in csv.DictReader(f)}

with open(os.path.join(DATASET_DIR, "user_audit_log.csv"), "r", encoding="utf-8") as f:
    audit_logs = list(csv.DictReader(f))

hist_emails = {}
all_user_emails = defaultdict(set)
all_user_hashes = defaultdict(set)

for u, r in users_by_id.items():
    all_user_emails[u].add(r["email"].lower())
    if r["email_hash"]:
        all_user_hashes[u].add(r["email_hash"].lower())

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

with open(os.path.join(DATASET_DIR, "evidence_files.csv"), "r", encoding="utf-8") as f:
    evidence_files = list(csv.DictReader(f))

# Pre-read all evidence files into memory
ev_contents = {}
for e in evidence_files:
    fpath = os.path.join(DATASET_DIR, e["file_path"].replace("/", os.sep))
    if os.path.exists(fpath):
        if fpath.endswith(".pdf"):
            try:
                reader = PdfReader(fpath)
                text = "\n".join(p.extract_text() for p in reader.pages)
                ev_contents[e["file_id"]] = text.lower()
            except Exception:
                ev_contents[e["file_id"]] = ""
        elif fpath.endswith(".png"):
            # We already have the text of all 11 pngs, but let's check
            ev_contents[e["file_id"]] = ""
        else:
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
                    ev_contents[e["file_id"]] = fp.read().lower()
            except Exception:
                ev_contents[e["file_id"]] = ""

with open(os.path.join(DATASET_DIR, "sample_deletion_requests.csv"), "r", encoding="utf-8") as f:
    sample_requests = list(csv.DictReader(f))

with open(os.path.join(DATASET_DIR, "sample_output.csv"), "r", encoding="utf-8") as f:
    sample_outputs = {r["case_id"]: r for r in csv.DictReader(f)}

print(f"{'Case':<8} | {'Expected Evidence':<30} | {'Matched Evidence Files (<= audit_at)'}")
print("-" * 100)

for req in sample_requests:
    cid = req["case_id"]
    email = req["email"].lower()
    uid = identities.get(email, {}).get("user_id") or hist_emails.get(email)
    audit_at = req["audit_at"]
    
    # Expected evs
    expected_steps = json.loads(sample_outputs[cid]["steps_json"])
    expected_evs = set(s["evidence_id"] for s in expected_steps if s["evidence_id"])
    
    # Find matching evidence files
    matched_evs = []
    user_identifiers = set()
    if uid:
        user_identifiers.add(uid.lower())
        user_identifiers.update(all_user_emails[uid])
        user_identifiers.update(all_user_hashes[uid])
    else:
        user_identifiers.add(email)
    
    for e in evidence_files:
        eid = e["file_id"]
        if e["captured_at"] <= audit_at:
            content = ev_contents.get(eid, "")
            # Check if any identifier is in content
            for ident in user_identifiers:
                if len(ident) > 3 and ident in content:
                    matched_evs.append(eid)
                    break
    
    match_str = ", ".join(matched_evs)
    exp_str = ", ".join(sorted(expected_evs))
    print(f"{cid:<8} | {exp_str:<30} | {match_str}")
