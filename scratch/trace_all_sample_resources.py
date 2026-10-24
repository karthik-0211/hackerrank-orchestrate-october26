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

with open(os.path.join(DATASET_DIR, "system_activity.csv"), "r", encoding="utf-8") as f:
    activities = list(csv.DictReader(f))

with open(os.path.join(DATASET_DIR, "evidence_files.csv"), "r", encoding="utf-8") as f:
    manifest = {r["file_id"]: r for r in csv.DictReader(f)}

# Let's see: for each sample case, what are all the resources in sample_output?
all_sample_resources = {}
for cid, row in sample_outputs.items():
    steps = json.loads(row["steps_json"])
    all_sample_resources[cid] = set(s["resource_id"] for s in steps)

# For each resource, check where it appears in system_activity
act_by_res = {}
for a in activities:
    res = a["resource_id"]
    if res not in act_by_res:
        act_by_res[res] = []
    act_by_res[res].append(a)

for cid in sorted(sample_requests.keys(), key=lambda x: int(x.split('_')[1])):
    req = sample_requests[cid]
    res_set = all_sample_resources[cid]
    print(f"\n--- {cid} ({req['email']}) audit_at={req['audit_at']} status={sample_outputs[cid]['deletion_status']} ---")
    for res in sorted(res_set):
        acts = act_by_res.get(res, [])
        act_types = [f"{a['event_type']}:{a['reported_result']}@{a['event_time']}" for a in acts]
        print(f"  Resource: {res:<20} | Acts ({len(acts)}): {'; '.join(act_types[:3])}")
