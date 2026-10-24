import csv
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

# Let's search where account_410, account_3136, etc. appear in system_activity.csv
test_resources = ["account_410", "account_3136", "account_5482", "audit_record_451", "audit_record_9265", "backup_838", "data_flow_2337", "analytics_6077", "support_2351"]

with open(os.path.join(DATASET_DIR, "system_activity.csv"), "r", encoding="utf-8") as f:
    activities = list(csv.DictReader(f))

for res in test_resources:
    matches = [a for a in activities if a["resource_id"] == res or res in a["details"]]
    print(f"\nResource {res} in system_activity ({len(matches)} matches):")
    for m in matches:
        print(f"  {m['activity_id']} | {m['event_time']} | {m['event_type']} | {m['source_system']} -> {m['target_system']} | res={m['resource_id']} | res_result={m['reported_result']} | details={m['details']}")
