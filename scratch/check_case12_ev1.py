import os

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

ev1_path = os.path.join(DATASET_DIR, "evidence", "logs", "service_events_ap_south_20260915.log")
with open(ev1_path, "r", encoding="utf-8") as f:
    for line in f:
        if "minjun" in line.lower() or "user_12" in line.lower() or "9797" in line or "2945" in line or "9914" in line:
            print(line.strip())
