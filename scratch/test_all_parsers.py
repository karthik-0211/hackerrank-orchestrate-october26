import os
import glob
import sqlite3
import json
from pypdf import PdfReader

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

# 1. SQL
sql_files = glob.glob(os.path.join(DATASET_DIR, "evidence", "databases", "*.sql"))
print(f"Testing {len(sql_files)} SQL files...")
sql_success = 0
for f in sql_files:
    try:
        conn = sqlite3.connect(":memory:")
        with open(f, "r", encoding="utf-8", errors="ignore") as fp:
            conn.executescript(fp.read())
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        conn.close()
        sql_success += 1
    except Exception as e:
        print(f"SQL Error in {os.path.basename(f)}: {e}")
print(f"SQL success: {sql_success}/{len(sql_files)}")

# 2. JSON
json_files = glob.glob(os.path.join(DATASET_DIR, "evidence", "records", "*.json"))
print(f"Testing {len(json_files)} JSON files...")
json_success = 0
for f in json_files:
    try:
        with open(f, "r", encoding="utf-8", errors="ignore") as fp:
            d = json.load(fp)
        json_success += 1
    except Exception as e:
        print(f"JSON Error in {os.path.basename(f)}: {e}")
print(f"JSON success: {json_success}/{len(json_files)}")

# 3. PDF
pdf_files = glob.glob(os.path.join(DATASET_DIR, "evidence", "documents", "*.pdf"))
print(f"Testing {len(pdf_files)} PDF files...")
pdf_success = 0
for f in pdf_files:
    try:
        reader = PdfReader(f)
        text = "\n".join(p.extract_text() for p in reader.pages)
        pdf_success += 1
    except Exception as e:
        print(f"PDF Error in {os.path.basename(f)}: {e}")
print(f"PDF success: {pdf_success}/{len(pdf_files)}")

# 4. LOG and TXT
log_files = glob.glob(os.path.join(DATASET_DIR, "evidence", "logs", "*.log"))
txt_files = glob.glob(os.path.join(DATASET_DIR, "evidence", "records", "*.txt"))
print(f"Testing {len(log_files)} LOG files and {len(txt_files)} TXT files...")
