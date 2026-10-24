import os

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

target = "account_004"
for root, dirs, files in os.walk(DATASET_DIR):
    for f in files:
        if f.endswith(".py"):
            continue
        fpath = os.path.join(root, f)
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
                if target in fp.read():
                    print(f"Found {target} in {os.path.relpath(fpath, DATASET_DIR)}")
        except Exception:
            pass
