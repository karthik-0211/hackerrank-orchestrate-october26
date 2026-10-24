import csv
import json
import os
import re
import sqlite3
import sys
from collections import defaultdict
from pypdf import PdfReader

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

with open(os.path.join(DATASET_DIR, "evidence_files.csv"), "r", encoding="utf-8") as f:
    evidence_manifest = list(csv.DictReader(f))

print(f"Total evidence files in manifest: {len(evidence_manifest)}")

# Data structure to hold extracted evidence records
# record: {
#   "file_id": ...,
#   "file_path": ...,
#   "captured_at": ...,
#   "system_id": ...,
#   "resource_id": ...,
#   "record_type": ...,
#   "status": ..., # FOUND, NOT_FOUND, ACTIVE, DISABLED, BLOCKED, REDACTED, ANONYMIZED, IDENTIFIABLE, etc.
#   "identifiers": set([...]), # emails, user_ids, phones, hashes
#   "raw": ...
# }
extracted_records = []

# 1. Parse JSON files
for ev in evidence_manifest:
    fpath = os.path.join(DATASET_DIR, ev["file_path"].replace("/", os.sep))
    if not os.path.exists(fpath):
        continue
    eid = ev["file_id"]
    cap_at = ev["captured_at"]

    if fpath.endswith(".json"):
        try:
            with open(fpath, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            
            # Type A: service_exports (e.g. evidence_92)
            if isinstance(data, dict) and "service_exports" in data:
                sexports = data["service_exports"]
                for sys_id, sys_data in sexports.items():
                    # account_service: profile_lookups
                    if sys_id == "account_service" and "profile_lookups" in sys_data:
                        for item in sys_data["profile_lookups"]:
                            rid = item.get("resource_id")
                            sc = item.get("status_code")
                            status = "NOT_FOUND" if sc == 404 else "FOUND"
                            prof = item.get("profile") or {}
                            idents = set()
                            for k in ["customer_reference", "email", "phone", "email_hash"]:
                                if prof.get(k):
                                    idents.add(str(prof[k]).lower())
                            extracted_records.append({
                                "file_id": eid, "captured_at": cap_at, "system_id": sys_id,
                                "resource_id": rid, "record_type": "USER_PROFILE", "status": status,
                                "identifiers": idents, "raw": item
                            })
                    # security_service: audit_log_lookups / audit_logs
                    elif sys_id == "security_service":
                        records = sys_data.get("audit_log_lookups") or sys_data.get("records") or []
                        for item in records:
                            rid = item.get("resource_id")
                            sc = item.get("status_code", 200)
                            status = "FOUND" if sc == 200 else "NOT_FOUND"
                            rec = item.get("audit_log") or item.get("record") or item
                            idents = set()
                            for k in ["subject_reference", "customer_reference", "user_id"]:
                                if rec.get(k):
                                    idents.add(str(rec[k]).lower())
                            extracted_records.append({
                                "file_id": eid, "captured_at": cap_at, "system_id": sys_id,
                                "resource_id": rid, "record_type": "SECURITY_AUDIT_LOG", "status": status,
                                "identifiers": idents, "raw": item
                            })
                    # support_platform: support_lookups / tickets
                    elif sys_id == "support_platform":
                        records = sys_data.get("support_lookups") or sys_data.get("tickets") or []
                        for item in records:
                            rid = item.get("resource_id")
                            sc = item.get("status_code", 200)
                            msg = item.get("ticket") or item.get("message") or item
                            # check if redacted or identifiable
                            idents = set()
                            for k in ["customer_reference", "email", "phone", "user_id"]:
                                if msg.get(k):
                                    idents.add(str(msg[k]).lower())
                            # if email or phone or name present -> IDENTIFIABLE, else REDACTED
                            has_pii = bool(msg.get("email") or msg.get("phone") or msg.get("customer_name") or msg.get("full_name"))
                            status = "IDENTIFIABLE" if has_pii else "REDACTED"
                            extracted_records.append({
                                "file_id": eid, "captured_at": cap_at, "system_id": sys_id,
                                "resource_id": rid, "record_type": "SUPPORT_MESSAGE", "status": status,
                                "identifiers": idents, "raw": item
                            })
                    # analytics_platform: analytics_lookups / profiles
                    elif sys_id == "analytics_platform":
                        records = sys_data.get("analytics_lookups") or sys_data.get("profiles") or []
                        for item in records:
                            rid = item.get("resource_id")
                            prof = item.get("analytics_profile") or item.get("profile") or item
                            idents = set()
                            for k in ["user_id", "email", "phone", "email_hash", "customer_reference"]:
                                if prof.get(k):
                                    idents.add(str(prof[k]).lower())
                            has_pii = bool(prof.get("email") or prof.get("phone") or prof.get("user_id") or prof.get("email_hash"))
                            status = "IDENTIFIABLE" if has_pii else "ANONYMIZED"
                            extracted_records.append({
                                "file_id": eid, "captured_at": cap_at, "system_id": sys_id,
                                "resource_id": rid, "record_type": "ANALYTICS_PROFILE", "status": status,
                                "identifiers": idents, "raw": item
                            })
                    # integration_service: data_flows
                    elif sys_id == "integration_service":
                        records = sys_data.get("connectors") or sys_data.get("data_flows") or []
                        for item in records:
                            rid = item.get("resource_id")
                            flow_status = item.get("status") or item.get("flow_status")
                            # active vs disabled
                            status = "ACTIVE" if str(flow_status).upper() in ["ACTIVE", "ENABLED", "RUNNING"] else "DISABLED"
                            idents = set()
                            for k in ["selector", "correlation_key", "customer_reference", "user_id"]:
                                if item.get(k):
                                    idents.add(str(item[k]).lower())
                            extracted_records.append({
                                "file_id": eid, "captured_at": cap_at, "system_id": sys_id,
                                "resource_id": rid, "record_type": "DATA_FLOW", "status": status,
                                "identifiers": idents, "raw": item
                            })
                    # backup_service: backups / archives
                    elif sys_id == "backup_service":
                        records = sys_data.get("archives") or sys_data.get("backups") or []
                        for item in records:
                            rid = item.get("resource_id")
                            b_status = item.get("status") or item.get("restore_access") or item.get("restore_status")
                            status = "BLOCKED" if str(b_status).upper() in ["BLOCKED", "RESTRICTED", "DISABLED"] else "ACTIVE"
                            idents = set()
                            for k in ["customer_reference", "user_id", "selector", "archive_user"]:
                                if item.get(k):
                                    idents.add(str(item[k]).lower())
                            extracted_records.append({
                                "file_id": eid, "captured_at": cap_at, "system_id": sys_id,
                                "resource_id": rid, "record_type": "BACKUP_ARCHIVE", "status": status,
                                "identifiers": idents, "raw": item
                            })
                    # search_service: search_documents / index_entries
                    elif sys_id == "search_service":
                        records = sys_data.get("documents") or sys_data.get("index_entries") or []
                        for item in records:
                            rid = item.get("resource_id")
                            sc = item.get("status_code", 200)
                            status = "FOUND" if sc == 200 else "NOT_FOUND"
                            doc = item.get("document") or item
                            idents = set()
                            for k in ["customer_reference", "email", "user_id"]:
                                if doc.get(k):
                                    idents.add(str(doc[k]).lower())
                            extracted_records.append({
                                "file_id": eid, "captured_at": cap_at, "system_id": sys_id,
                                "resource_id": rid, "record_type": "SEARCH_INDEX_ENTRY", "status": status,
                                "identifiers": idents, "raw": item
                            })
                    # export_service: exports
                    elif sys_id == "export_service":
                        records = sys_data.get("exports") or sys_data.get("jobs") or []
                        for item in records:
                            rid = item.get("resource_id")
                            sc = item.get("status_code", 200)
                            status = "FOUND" if sc == 200 else "NOT_FOUND"
                            exp = item.get("export") or item
                            idents = set()
                            for k in ["customer_reference", "email", "user_id"]:
                                if exp.get(k):
                                    idents.add(str(exp[k]).lower())
                            extracted_records.append({
                                "file_id": eid, "captured_at": cap_at, "system_id": sys_id,
                                "resource_id": rid, "record_type": "USER_EXPORT", "status": status,
                                "identifiers": idents, "raw": item
                            })

            # Type B: snapshots (e.g. evidence_51)
            elif isinstance(data, dict) and "snapshots" in data:
                for s in data["snapshots"]:
                    ds = s.get("data_store")
                    records = s.get("records", [])
                    for item in records:
                        rid = item.get("resource_id")
                        idents = set()
                        for k in ["subject_reference", "user_id", "email", "phone", "email_hash", "customer_reference"]:
                            if item.get(k):
                                idents.add(str(item[k]).lower())
                        
                        if ds == "identity_service":
                            # Tombstone
                            has_pii = bool(item.get("name") or item.get("email") or item.get("phone") or item.get("email_hash"))
                            status = "IDENTIFIABLE" if has_pii else "REDACTED"
                            extracted_records.append({
                                "file_id": eid, "captured_at": cap_at, "system_id": ds,
                                "resource_id": rid, "record_type": "ACCOUNT_TOMBSTONE", "status": status,
                                "identifiers": idents, "raw": item
                            })
                        elif ds == "security_service":
                            extracted_records.append({
                                "file_id": eid, "captured_at": cap_at, "system_id": ds,
                                "resource_id": rid, "record_type": "SECURITY_AUDIT_LOG", "status": "FOUND",
                                "identifiers": idents, "raw": item
                            })
                        elif ds == "account_service":
                            extracted_records.append({
                                "file_id": eid, "captured_at": cap_at, "system_id": ds,
                                "resource_id": rid, "record_type": "USER_PROFILE", "status": "FOUND",
                                "identifiers": idents, "raw": item
                            })

            # Type C: records (e.g. evidence_56, evidence_59)
            elif isinstance(data, dict) and "records" in data:
                coll = data.get("collection", "")
                src = data.get("source", "")
                for item in data["records"]:
                    rid = item.get("resource_id")
                    idents = set()
                    for k in ["user_id", "email", "phone", "email_hash", "customer_reference"]:
                        if item.get(k):
                            idents.add(str(item[k]).lower())
                    if "analytics" in coll or "analytics" in src:
                        has_pii = bool(item.get("user_id") or item.get("email") or item.get("phone") or item.get("email_hash"))
                        status = "IDENTIFIABLE" if has_pii else "ANONYMIZED"
                        extracted_records.append({
                            "file_id": eid, "captured_at": cap_at, "system_id": "analytics_platform",
                            "resource_id": rid, "record_type": "ANALYTICS_PROFILE", "status": status,
                            "identifiers": idents, "raw": item
                        })
                    elif "export" in coll or "export" in src:
                        extracted_records.append({
                            "file_id": eid, "captured_at": cap_at, "system_id": "export_service",
                            "resource_id": rid, "record_type": "USER_EXPORT", "status": "FOUND",
                            "identifiers": idents, "raw": item
                        })

        except Exception as e:
            print(f"Error parsing JSON {eid}: {e}")

print(f"Total extracted records so far: {len(extracted_records)}")
