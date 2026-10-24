import os

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

ev5_path = os.path.join(DATASET_DIR, "evidence", "databases", "customer_data_read_replica_20260921.sql")
with open(ev5_path, "r", encoding="utf-8") as f:
    ev5_content = f.read()

for email in ["diya.k4436@outlook.com", "seoyeon-han@gmail.com"]:
    print(f"Does evidence_05 contain {email}? {'YES' if email in ev5_content else 'NO'}")
    for line in ev5_content.splitlines():
        if email in line:
            print(f"  Line: {line}")
