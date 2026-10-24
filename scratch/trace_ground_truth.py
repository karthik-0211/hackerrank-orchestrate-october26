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
    out = outputs[cid]
    steps = json.loads(out['steps_json'])
    resources = [(step['phase'], step['system_id'], step['resource_id'], step['operation'], step['state'], step['evidence_id']) for step in steps]
    print(f"{cid} | Status: {out['deletion_status']:<12} | Steps: {len(steps)}")
    for r in resources:
        print(f"   {r[0]:<12} | {r[1]:<20} | {r[2]:<20} | {r[3]:<26} | {r[4]:<10} | {r[5]}")
