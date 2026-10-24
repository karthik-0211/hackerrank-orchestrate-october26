import csv
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

samples = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_deletion_requests.csv'), encoding='utf-8')))
outputs = {r['case_id']: r for r in csv.DictReader(open(os.path.join(DATASET_DIR, 'sample_output.csv'), encoding='utf-8'))}
activities = list(csv.DictReader(open(os.path.join(DATASET_DIR, 'system_activity.csv'), encoding='utf-8')))

for s in samples[:10]:
    cid = s['case_id']
    req_at = s['requested_at']
    rep_at = s['reported_at']
    aud_at = s['audit_at']
    
    # Expected resources
    steps = json.loads(outputs[cid]['steps_json'])
    exp_res = set((st['system_id'], st['resource_id']) for st in steps)
    
    # Find activities in time window [req_at - 1h, rep_at + 1h]
    # filter for deletion_worker or related
    cand_acts = []
    for a in activities:
        etime = a['event_time']
        if req_at <= etime <= rep_at:
            if a['source_system'] in ['deletion_worker', 'security_service', 'integration_service', 'backup_service'] or a['event_type'] in ['DELETE_RECORD', 'REDACT_RECORD', 'ANONYMIZE_RECORD', 'RETAIN_RECORD', 'DISABLE_DATA_FLOW', 'BLOCK_RESTORE']:
                cand_acts.append((a['event_time'], a['target_system'], a['resource_id'], a['event_type'], a['reported_result']))
    
    print(f"\n{cid} (req: {req_at}, rep: {rep_at})")
    print(f"  Expected resources: {sorted(exp_res)}")
    print(f"  Activities in [req, rep] ({len(cand_acts)}):")
    for ca in cand_acts[-5:]: # show last 5
        print(f"    {ca}")
