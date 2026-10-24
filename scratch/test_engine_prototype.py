import csv
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

samples = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_deletion_requests.csv'), encoding='utf-8')))
outputs = {r['case_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_output.csv'), encoding='utf-8'))}

for s in samples:
    cid = s['case_id']
    steps = json.loads(outputs[cid]['steps_json'])
    evs = sorted(list(set(st['evidence_id'] for st in steps if st['evidence_id'])))
    rep_status = s['reported_status']
    del_status = outputs[cid]['deletion_status']
    print(f"{cid:<8} | reported: {rep_status:<18} -> actual: {del_status:<12} | cited: {evs}")
