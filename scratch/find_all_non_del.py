import csv
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

with open(os.path.join(DATASET_DIR, "deletion_requests.csv"), "r", encoding="utf-8") as f:
    all_requests = list(csv.DictReader(f))

# Let's check for negative phrases:
# "not asking for deletion", "not a request to erase", "leave the account active", "do not close",
# "keep the account", "without removing", "marketing lists only", "continue using"
# Also check if any request does not ask for deletion.

not_del = []
for r in all_requests:
    text = r["request_text"].lower()
    # Check explicit non-deletion signals
    has_neg = any(p in text for p in [
        "not asking for deletion", "not a request to erase", "leave the account active",
        "do not close", "keep the account", "without removing", "marketing lists only",
        "continue using", "leave my profile", "don't delete", "not to erase"
    ])
    if has_neg:
        not_del.append((r['case_id'], r['request_text']))

print(f"Explicit non-deletion requests found: {len(not_del)}")
for cid, txt in not_del:
    print(f"  {cid}: {txt}")
