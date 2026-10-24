import json
import os

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

with open(os.path.join(DATASET_DIR, "evidence", "records", "service_resource_export_20260915_114455.json"), "r", encoding="utf-8") as f:
    data = json.load(f)

# Search for audit_record_9265 in data
def search_dict(d, target):
    if isinstance(d, dict):
        for k, v in d.items():
            if v == target or (isinstance(v, str) and target in v):
                print(f"Match: {d}")
            search_dict(v, target)
    elif isinstance(d, list):
        for item in d:
            search_dict(item, target)

search_dict(data, "audit_record_9265")
