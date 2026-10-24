import csv
import json
import os
import glob
from collections import defaultdict, Counter

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

# 1. Load sample deletion requests
with open(os.path.join(DATASET_DIR, "sample_deletion_requests.csv"), "r", encoding="utf-8") as f:
    sample_requests = list(csv.DictReader(f))

# 2. Load sample outputs
with open(os.path.join(DATASET_DIR, "sample_output.csv"), "r", encoding="utf-8") as f:
    sample_outputs = list(csv.DictReader(f))

print(f"Loaded {len(sample_requests)} sample requests and {len(sample_outputs)} sample outputs.")

# Analyze statuses in sample_output
status_counts = Counter(r["deletion_status"] for r in sample_outputs)
print(f"Sample output status counts: {status_counts}")

# Check step counts and operations in sample_output
op_counts = Counter()
phase_counts = Counter()
evidence_refs = Counter()
systems_seen = Counter()

for row in sample_outputs:
    steps = json.loads(row["steps_json"])
    for step in steps:
        op_counts[step["operation"]] += 1
        phase_counts[step["phase"]] += 1
        systems_seen[step["system_id"]] += 1
        if step["evidence_id"]:
            evidence_refs[step["evidence_id"]] += 1

print("\nPhases in sample output:")
for p, c in phase_counts.items():
    print(f"  {p}: {c}")

print("\nOperations in sample output:")
for op, c in op_counts.items():
    print(f"  {op}: {c}")

print("\nSystems in sample output:")
for sys, c in systems_seen.items():
    print(f"  {sys}: {c}")

print("\nEvidence IDs in sample output:")
for ev, c in evidence_refs.items():
    print(f"  {ev}: {c}")
