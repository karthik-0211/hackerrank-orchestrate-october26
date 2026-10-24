import os

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

ev1_path = os.path.join(DATASET_DIR, "evidence", "logs", "service_events_ap_south_20260915.log")
with open(ev1_path, "r", encoding="utf-8") as f:
    for line in f:
        if "lucia" in line.lower() or "user_15" in line.lower() or "4745" in line or "1596" in line or "9846" in line:
            print(line.strip())
