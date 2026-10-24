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

with open(os.path.join(DATASET_DIR, "evidence_files.csv"), "r", encoding="utf-8") as f:
    evidence_files = {r["file_id"]: r for r in csv.DictReader(f)}

print(f"{'Case':<8} | {'Email':<28} | {'Audit_at':<20} | {'Reported':<18} | {'Evidence cited':<35} | {'Evidence captured_at'}")
print("-" * 125)

for case_id, req in sample_requests.items():
    steps = json.loads(sample_outputs[case_id]["steps_json"])
    ev_ids = sorted(list(set(s["evidence_id"] for s in steps if s["evidence_id"])))
    ev_info = []
    for eid in ev_ids:
        capt = evidence_files[eid]["captured_at"]
        path = os.path.basename(evidence_files[eid]["file_path"])
        ev_info.append(f"{eid} ({path}, {capt})")
    print(f"{case_id:<8} | {req['email']:<28} | {req['audit_at']:<20} | {req['reported_status']:<18} | {', '.join(ev_ids):<35} | {'; '.join(ev_info)}")
