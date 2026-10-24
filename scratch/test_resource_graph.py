import csv
import json
import os
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

# 1. Load known resource tags from all evidence files
# Map resource_id -> set of user identifiers (user_ids, emails)
from code.evidence_indexer import EvidenceIndexer
indexer = EvidenceIndexer(DATASET_DIR)

res_known_users = defaultdict(set)
for obs in indexer.observations:
    if obs.identifiers and obs.resource_id:
        for ident in obs.identifiers:
            if ident.startswith("user_") or "@" in ident:
                res_known_users[obs.resource_id].add(ident)

print(f"Total resources with direct evidence tags: {len(res_known_users)}")

# 2. Build graph from system_activity.csv
with open(os.path.join(DATASET_DIR, "system_activity.csv"), "r", encoding="utf-8") as f:
    activities = list(csv.DictReader(f))

# Group activities by time windows (e.g. 5 minutes)
worker_acts = [a for a in activities if a["source_system"] in ["deletion_worker", "archive_service", "security_service"] or a["event_type"] in ["DELETE_RECORD", "REDACT_RECORD", "ANONYMIZE_RECORD", "RETAIN_RECORD", "DISABLE_DATA_FLOW", "BLOCK_RESTORE"]]

adj = defaultdict(set)
for i in range(len(worker_acts)):
    a1 = worker_acts[i]
    r1 = a1["resource_id"]
    t1 = a1["event_time"]
    for j in range(i + 1, min(len(worker_acts), i + 10)):
        a2 = worker_acts[j]
        r2 = a2["resource_id"]
        t2 = a2["event_time"]
        # If within 45 seconds of each other
        # rough diff
        if t1[:10] == t2[:10] and abs((int(t2[11:13])*3600 + int(t2[14:16])*60 + int(t2[17:19])) - (int(t1[11:13])*3600 + int(t1[14:16])*60 + int(t1[17:19]))) <= 45:
            # Different systems -> same workflow step!
            if a1["target_system"] != a2["target_system"]:
                adj[r1].add(r2)
                adj[r2].add(r1)

# Connected components
visited = set()
components = []
for r in list(adj.keys()):
    if r not in visited:
        comp = []
        q = [r]
        visited.add(r)
        while q:
            curr = q.pop(0)
            comp.append(curr)
            for nxt in adj[curr]:
                if nxt not in visited:
                    visited.add(nxt)
                    q.append(nxt)
        components.append(comp)

print(f"Total connected resource components: {len(components)}")

# Propagate user tags through components
comp_user_map = {}
for comp in components:
    users_in_comp = set()
    for r in comp:
        users_in_comp.update(res_known_users.get(r, set()))
    if users_in_comp:
        for r in comp:
            res_known_users[r].update(users_in_comp)

# Test sample cases 21 to 32
for r in ['account_6440', 'analytics_5335', 'account_3136', 'analytics_1895', 'account_5684', 'analytics_4566', 'account_3866', 'analytics_4574', 'account_5482', 'analytics_6077']:
    print(f"  {r}: resolved users = {res_known_users.get(r)}")
