import csv
import os
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

with open(os.path.join(DATASET_DIR, "deletion_requests.csv"), "r", encoding="utf-8") as f:
    all_requests = list(csv.DictReader(f))

# Check for non-ASCII or non-English
non_english = []
for r in all_requests:
    text = r["request_text"]
    # If text contains non-ascii characters or specific non-english tokens
    if any(ord(c) > 127 for c in text):
        non_english.append((r['case_id'], text))

print(f"Non-ASCII request count: {len(non_english)}")
for cid, txt in non_english[:20]:
    print(f"  {cid}: {txt[:80]}...")
