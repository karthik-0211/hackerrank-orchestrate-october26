import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")
log_dir = os.path.join(DATASET_DIR, "evidence", "logs")

for f in sorted(os.listdir(log_dir)):
    if not f.endswith(".log"):
        continue
    fpath = os.path.join(log_dir, f)
    with open(fpath, "r", encoding="utf-8") as fp:
        lines = [line.strip() for line in fp if line.strip()]
    print(f"\n--- {f} ({len(lines)} lines) ---")
    for l in lines[:3]:
        print(f"  {l[:120]}")
