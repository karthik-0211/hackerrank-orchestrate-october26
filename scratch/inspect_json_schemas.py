import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")
rec_dir = os.path.join(DATASET_DIR, "evidence", "records")

for f in sorted(os.listdir(rec_dir)):
    if not f.endswith(".json"):
        continue
    fpath = os.path.join(rec_dir, f)
    with open(fpath, "r", encoding="utf-8") as fp:
        try:
            data = json.load(fp)
            keys = list(data.keys()) if isinstance(data, dict) else f"list({len(data)})"
            prefix = f.split("_2026")[0] if "_2026" in f else f
            print(f"{f:<45} | keys: {keys}")
        except Exception as e:
            print(f"{f:<45} | ERROR: {e}")
