import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")
db_dir = os.path.join(DATASET_DIR, "evidence", "databases")

for f in sorted(os.listdir(db_dir)):
    if not f.endswith(".sql"):
        continue
    fpath = os.path.join(db_dir, f)
    with open(fpath, "r", encoding="utf-8") as fp:
        sql = fp.read()
    tables = re.findall(r"CREATE TABLE (\w+)", sql)
    inserts = re.findall(r"INSERT INTO \"?(\w+)\"?", sql)
    print(f"{f:<50} | tables: {tables} | inserts: {len(inserts)}")
