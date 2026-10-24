import csv
import json
import os
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

with open(os.path.join(DATASET_DIR, "evidence_files.csv"), "r", encoding="utf-8") as f:
    ev_files = list(csv.DictReader(f))

# Sort evidence files by captured_at
ev_files_sorted = sorted(ev_files, key=lambda x: x["captured_at"])

with open(os.path.join(DATASET_DIR, "sample_deletion_requests.csv"), "r", encoding="utf-8") as f:
    samples = list(csv.DictReader(f))

with open(os.path.join(DATASET_DIR, "sample_output.csv"), "r", encoding="utf-8") as f:
    sample_outputs = {r["case_id"]: r for r in csv.DictReader(f)}

with open(os.path.join(DATASET_DIR, "deletion_requests.csv"), "r", encoding="utf-8") as f:
    eval_requests = list(csv.DictReader(f))

all_requests = samples + eval_requests
requests_by_audit = defaultdict(list)
for r in all_requests:
    requests_by_audit[r["audit_at"]].append(r)

print(f"Total requests: {len(all_requests)}, Unique audit_at timestamps: {len(requests_by_audit)}")

# Check for each audit_at what evidence files are eligible (captured_at <= audit_at)
for audit_at in sorted(requests_by_audit.keys())[:15]:
    reqs = requests_by_audit[audit_at]
    cids = [r["case_id"] for r in reqs]
    # eligible evs
    eligible = [e for e in ev_files_sorted if e["captured_at"] <= audit_at]
    latest_3 = eligible[-3:] if len(eligible) >= 3 else eligible
    print(f"\naudit_at: {audit_at} ({len(reqs)} cases: {cids[:3]}...{cids[-1:]})")
    print(f"  Total eligible evidence files: {len(eligible)}")
    print(f"  Latest eligible evidence files:")
    for le in latest_3:
        print(f"    {le['file_id']}: {le['captured_at']} | {le['file_path']}")
