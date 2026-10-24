import csv
import json
import os
import re
import sys
from pypdf import PdfReader

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

with open(os.path.join(DATASET_DIR, "evidence_files.csv"), "r", encoding="utf-8") as f:
    evidence_manifest = list(csv.DictReader(f))

print(f"Manifest contains {len(evidence_manifest)} files.")

# Count by file extension
ext_counts = {}
for e in evidence_manifest:
    ext = os.path.splitext(e["file_path"])[1].lower()
    ext_counts[ext] = ext_counts.get(ext, 0) + 1

print(f"Extensions: {ext_counts}")

# Test parsing each format
sql_files = [e for e in evidence_manifest if e["file_path"].endswith(".sql")]
json_files = [e for e in evidence_manifest if e["file_path"].endswith(".json")]
log_files = [e for e in evidence_manifest if e["file_path"].endswith(".log")]
txt_files = [e for e in evidence_manifest if e["file_path"].endswith(".txt")]
pdf_files = [e for e in evidence_manifest if e["file_path"].endswith(".pdf")]
png_files = [e for e in evidence_manifest if e["file_path"].endswith(".png")]

print(f"SQL: {len(sql_files)}, JSON: {len(json_files)}, LOG: {len(log_files)}, TXT: {len(txt_files)}, PDF: {len(pdf_files)}, PNG: {len(png_files)}")
