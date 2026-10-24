import os
import glob
import re

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

audit_locations = {}

for root, dirs, files in os.walk(DATASET_DIR):
    for f in files:
        if f.endswith(".py"):
            continue
        fpath = os.path.join(root, f)
        relpath = os.path.relpath(fpath, DATASET_DIR)
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
                content = fp.read()
                matches = set(re.findall(r"audit_record_\d+", content))
                if matches:
                    audit_locations[relpath] = len(matches)
        except Exception:
            pass

print("Files containing audit_record_...:")
for k, v in audit_locations.items():
    print(f"  {k}: {v} distinct audit records")
