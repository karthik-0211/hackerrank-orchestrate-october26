import csv
import json
import os
import re
import sys
import sqlite3
from collections import defaultdict
from pypdf import PdfReader

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

# 1. Load manifest
with open(os.path.join(DATASET_DIR, "evidence_files.csv"), "r", encoding="utf-8") as f:
    manifest = {r["file_id"]: r for r in csv.DictReader(f)}

print(f"Loaded {len(manifest)} manifest entries.")

# Load sample requests and sample outputs
with open(os.path.join(DATASET_DIR, "sample_deletion_requests.csv"), "r", encoding="utf-8") as f:
    sample_requests = {r["case_id"]: r for r in csv.DictReader(f)}

with open(os.path.join(DATASET_DIR, "sample_output.csv"), "r", encoding="utf-8") as f:
    sample_outputs = {r["case_id"]: r for r in csv.DictReader(f)}

# Let's inspect which evidence files were cited for each of the 32 sample cases
sample_evidence_by_case = {}
for case_id, row in sample_outputs.items():
    steps = json.loads(row["steps_json"])
    evs = set(s["evidence_id"] for s in steps if s["evidence_id"])
    sample_evidence_by_case[case_id] = evs

print("Sample evidence files per case:")
for c, evs in sample_evidence_by_case.items():
    print(f"  {c}: {evs}")
