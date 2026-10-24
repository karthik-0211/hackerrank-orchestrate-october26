import json
import os

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

with open(os.path.join(DATASET_DIR, "evidence", "records", "service_resource_export_20260915_114455.json"), "r", encoding="utf-8") as f:
    data = json.load(f)

for service_name, service_data in data.get("service_exports", {}).items():
    print(f"\nService: {service_name}")
    for k, records in service_data.items():
        if isinstance(records, list):
            for rec in records:
                s = json.dumps(rec)
                if "user_28" in s or "smartinez" in s or "5482" in s or "9265" in s or "2351" in s or "6077" in s or "2337" in s or "838" in s:
                    print(f"  [{k}] {rec}")
