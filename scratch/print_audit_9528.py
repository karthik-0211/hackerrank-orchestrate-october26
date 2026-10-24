import os

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

ev5_path = os.path.join(DATASET_DIR, "evidence", "databases", "customer_data_read_replica_20260921.sql")
with open(ev5_path, "r", encoding="utf-8") as f:
    for line in f:
        if "audit_record_9528" in line:
            print(f"Line: {line}")
