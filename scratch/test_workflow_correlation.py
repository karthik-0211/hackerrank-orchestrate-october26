import csv
import json
import os
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

with open(os.path.join(DATASET_DIR, "system_activity.csv"), "r", encoding="utf-8") as f:
    activities = list(csv.DictReader(f))

# Let's see: group activities into deletion workflows
# Deletion workflows run as bursts of activities from deletion_worker
# Let's inspect all deletion_worker activities
worker_acts = [a for a in activities if a["source_system"] in ["deletion_worker", "archive_service", "security_service"]]
print(f"Total deletion worker activities: {len(worker_acts)}")

# Group activities within 10 minutes of each other into bursts / batches
batches = []
curr_batch = []
for a in worker_acts:
    if not curr_batch:
        curr_batch.append(a)
    else:
        # compare times
        prev_t = curr_batch[-1]["event_time"]
        curr_t = a["event_time"]
        # diff in seconds
        # rough diff
        if prev_t[:10] == curr_t[:10] and abs((int(curr_t[11:13])*60 + int(curr_t[14:16])) - (int(prev_t[11:13])*60 + int(prev_t[14:16]))) <= 15:
            curr_batch.append(a)
        else:
            batches.append(curr_batch)
            curr_batch = [a]
if curr_batch:
    batches.append(curr_batch)

print(f"Total activity batches: {len(batches)}")
for b in batches[:10]:
    t0 = b[0]["event_time"]
    res_list = [f"{x['target_system']}:{x['resource_id']}" for x in b]
    print(f"Batch @ {t0} ({len(b)} events): {res_list}")
