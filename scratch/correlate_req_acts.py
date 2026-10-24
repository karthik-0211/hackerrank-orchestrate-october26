import csv
import json
import os
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

with open(os.path.join(DATASET_DIR, "sample_deletion_requests.csv"), "r", encoding="utf-8") as f:
    sample_requests = list(csv.DictReader(f))

with open(os.path.join(DATASET_DIR, "sample_output.csv"), "r", encoding="utf-8") as f:
    sample_outputs = {r["case_id"]: r for r in csv.DictReader(f)}

with open(os.path.join(DATASET_DIR, "system_activity.csv"), "r", encoding="utf-8") as f:
    activities = list(csv.DictReader(f))

# Let's inspect the correlation between (requested_at, reported_at) and activity timestamps
for req in sample_requests[:10]:
    cid = req["case_id"]
    email = req["email"]
    req_at = req["requested_at"]
    rep_at = req["reported_at"]
    rep_dt = datetime.fromisoformat(rep_at.replace("Z", "+00:00"))
    
    # Get all resources in expected output
    steps = json.loads(sample_outputs[cid]["steps_json"])
    expected_res = set(s["resource_id"] for s in steps)
    
    # Find all activities mentioning expected_res
    matching_acts = [a for a in activities if a["resource_id"] in expected_res]
    print(f"\n{cid} ({email}) req_at={req_at} rep_at={rep_at}")
    print(f"  Expected resources: {expected_res}")
    for a in matching_acts:
        print(f"    act: {a['activity_id']} @ {a['event_time']} | {a['event_type']} | {a['resource_id']} | {a['reported_result']}")
