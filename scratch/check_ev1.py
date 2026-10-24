import os

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

ev1_path = os.path.join(DATASET_DIR, "evidence", "logs", "service_events_ap_south_20260915.log")
with open(ev1_path, "r", encoding="utf-8") as f:
    ev1_content = f.read()

for email in ["minjun.kim@gmail.com", "lucia-torres@gmail.com", "leonie.g9352@outlook.com", "e.varga90@yahoo.com"]:
    print(f"Does evidence_01 contain {email}? {'YES' if email in ev1_content else 'NO'}")
    # Also print lines containing email
    for line in ev1_content.splitlines():
        if email in line:
            print(f"  Line: {line}")
