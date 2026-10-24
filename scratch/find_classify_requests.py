import csv
import os

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

with open(os.path.join(DATASET_DIR, "system_activity.csv"), "r", encoding="utf-8") as f:
    activities = list(csv.DictReader(f))

classify_events = [a for a in activities if a["event_type"] == "CLASSIFY_REQUEST" or "non-deletion" in a["details"]]
print(f"Total CLASSIFY_REQUEST / non-deletion events: {len(classify_events)}")
for a in classify_events[:15]:
    print(f"  {a['activity_id']} | {a['event_time']} | {a['resource_id']} | {a['details']}")
