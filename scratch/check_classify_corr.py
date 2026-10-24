import csv
import os

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

with open(os.path.join(DATASET_DIR, "deletion_requests.csv"), "r", encoding="utf-8") as f:
    reqs = {r["case_id"]: r for r in csv.DictReader(f)}

with open(os.path.join(DATASET_DIR, "system_activity.csv"), "r", encoding="utf-8") as f:
    activities = list(csv.DictReader(f))

classify_events = [a for a in activities if a["event_type"] == "CLASSIFY_REQUEST"]

print("Comparing cases 533-542 with classify events:")
for i, cid in enumerate([f"case_{c}" for c in range(533, 543)]):
    req = reqs[cid]
    ev = classify_events[i]
    print(f"{cid} req_at={req['requested_at']} rep_at={req['reported_at']} | ev_time={ev['event_time']} res={ev['resource_id']}")
