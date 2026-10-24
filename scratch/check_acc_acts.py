import csv
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

with open(os.path.join(DATASET_DIR, "sample_deletion_requests.csv"), "r", encoding="utf-8") as f:
    sample_requests = list(csv.DictReader(f))

with open(os.path.join(DATASET_DIR, "sample_output.csv"), "r", encoding="utf-8") as f:
    sample_outputs = {r["case_id"]: r for r in csv.DictReader(f)}

with open(os.path.join(DATASET_DIR, "system_activity.csv"), "r", encoding="utf-8") as f:
    activities = list(csv.DictReader(f))

# Map account_... in sample_outputs
for req in sample_requests[10:]:
    cid = req["case_id"]
    steps = json.loads(sample_outputs[cid]["steps_json"])
    accounts = [s["resource_id"] for s in steps if s["system_id"] == "account_service"]
    for acc in accounts:
        acc_acts = [a for a in activities if a["resource_id"] == acc and a["target_system"] == "account_service"]
        print(f"{cid} ({req['email']}) -> {acc}: {len(acc_acts)} acts in system_activity")
        for a in acc_acts:
            print(f"    act: {a['activity_id']} @ {a['event_time']} | {a['event_type']} | res={a['resource_id']} | {a['reported_result']}")
