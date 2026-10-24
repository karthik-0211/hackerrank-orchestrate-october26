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

with open(os.path.join(DATASET_DIR, "system_activity.csv"), "r", encoding="utf-8") as f:
    activities = list(csv.DictReader(f))

# Index activities by resource_id
act_by_res = {}
for a in activities:
    res = a["resource_id"]
    if res not in act_by_res:
        act_by_res[res] = []
    act_by_res[res].append(a)

for case_id, req in sample_requests.items():
    steps = json.loads(sample_outputs[case_id]["steps_json"])
    print(f"\n==================== {case_id} ({req['email']}) ====================")
    for s in steps:
        res = s["resource_id"]
        in_act = len(act_by_res.get(res, []))
        act_summary = ""
        if in_act:
            a = act_by_res[res][0]
            act_summary = f"[act: {a['event_type']} {a['source_system']}->{a['target_system']} {a['reported_result']} @ {a['event_time']}]"
        print(f"  {s['phase']} | {s['system_id']} | {res} | {s['operation']} | {s['state']} | ev={s['evidence_id']} {act_summary}")
