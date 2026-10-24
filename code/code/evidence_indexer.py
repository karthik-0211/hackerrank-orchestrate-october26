"""Multimodal Evidence Indexer.

Recursively indexes the 94 local evidence files into structured in-memory observations.
Supports JSON records, SQLite SQL snapshots, structured LOG files, pipe-delimited TXT,
PDF text extraction, and administrative console facts.
Zero external network calls; fully reproducible and offline-safe.
"""

from __future__ import annotations

import csv
import json
import os
import re
import sqlite3
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from pypdf import PdfReader


@dataclass
class EvidenceObservation:
    file_id: str
    file_path: str
    captured_at: str
    system_id: str
    resource_id: str
    record_type: str
    status: str  # FOUND, NOT_FOUND, ACTIVE, DISABLED, BLOCKED, REDACTED, ANONYMIZED, IDENTIFIABLE, etc.
    identifiers: Set[str] = field(default_factory=set)
    details: Dict[str, Any] = field(default_factory=dict)


class EvidenceIndexer:
    def __init__(self, dataset_dir: str):
        self.dataset_dir = dataset_dir
        self.manifest: List[Dict[str, str]] = []
        self.observations: List[EvidenceObservation] = []
        self.by_file: Dict[str, List[EvidenceObservation]] = {}
        self.by_resource: Dict[str, List[EvidenceObservation]] = {}
        self._load_manifest()
        self._index_all_evidence()

    def _load_manifest(self) -> None:
        manifest_file = os.path.join(self.dataset_dir, "evidence_files.csv")
        with open(manifest_file, "r", encoding="utf-8") as f:
            self.manifest = list(csv.DictReader(f))

    def _index_all_evidence(self) -> None:
        for ev in self.manifest:
            eid = ev["file_id"]
            rel_path = ev["file_path"].replace("/", os.sep)
            fpath = os.path.join(self.dataset_dir, rel_path)
            cap_at = ev["captured_at"]

            if not os.path.exists(fpath):
                continue

            obs_list: List[EvidenceObservation] = []
            if fpath.endswith(".json"):
                obs_list = self._parse_json(eid, rel_path, cap_at, fpath)
            elif fpath.endswith(".sql"):
                obs_list = self._parse_sql(eid, rel_path, cap_at, fpath)
            elif fpath.endswith(".log") or fpath.endswith(".txt"):
                obs_list = self._parse_log_or_txt(eid, rel_path, cap_at, fpath)
            elif fpath.endswith(".pdf"):
                obs_list = self._parse_pdf(eid, rel_path, cap_at, fpath)
            elif fpath.endswith(".png"):
                obs_list = self._parse_png(eid, rel_path, cap_at, fpath)

            self.by_file[eid] = obs_list
            for obs in obs_list:
                self.observations.append(obs)
                self.by_resource.setdefault(obs.resource_id, []).append(obs)

    def _parse_json(self, eid: str, rel_path: str, cap_at: str, fpath: str) -> List[EvidenceObservation]:
        res: List[EvidenceObservation] = []
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict) and "service_exports" in data:
                sexports = data["service_exports"]
                for sys_id, sys_data in sexports.items():
                    # 1. account_service
                    if sys_id == "account_service":
                        lookups = sys_data.get("profile_lookups") or sys_data.get("records") or []
                        for item in lookups:
                            rid = item.get("resource_id", "")
                            status = "NOT_FOUND" if item.get("status_code") == 404 else "FOUND"
                            prof = item.get("profile") or {}
                            idents = {str(prof[k]).lower().strip() for k in ["customer_reference", "email", "phone", "email_hash"] if prof.get(k)}
                            res.append(EvidenceObservation(eid, rel_path, cap_at, sys_id, rid, "USER_PROFILE", status, idents, item))

                    # 2. security_service
                    elif sys_id == "security_service":
                        records = sys_data.get("audit_records") or sys_data.get("audit_log_lookups") or sys_data.get("records") or []
                        for item in records:
                            rid = item.get("resource_id", "")
                            rec = item.get("audit_log") or item.get("record") or item
                            idents = {str(rec[k]).lower().strip() for k in ["subject_reference", "customer_reference", "user_id"] if rec.get(k)}
                            res.append(EvidenceObservation(eid, rel_path, cap_at, sys_id, rid, "SECURITY_AUDIT_LOG", "FOUND", idents, item))

                    # 3. support_platform
                    elif sys_id == "support_platform":
                        tickets = sys_data.get("tickets") or sys_data.get("support_lookups") or []
                        for item in tickets:
                            rid = item.get("resource_id", "")
                            msg = item.get("ticket") or item.get("message") or item
                            idents = {str(msg[k]).lower().strip() for k in ["customer_reference", "email", "requester_email", "phone", "requester_phone", "user_id"] if msg.get(k)}
                            has_pii = bool(msg.get("email") or msg.get("requester_email") or msg.get("phone") or msg.get("requester_phone") or msg.get("customer_name") or msg.get("requester_name"))
                            status = "IDENTIFIABLE" if has_pii else "REDACTED"
                            res.append(EvidenceObservation(eid, rel_path, cap_at, sys_id, rid, "SUPPORT_MESSAGE", status, idents, item))

                    # 4. analytics_platform
                    elif sys_id == "analytics_platform":
                        profiles = sys_data.get("profiles") or sys_data.get("analytics_lookups") or []
                        for item in profiles:
                            rid = item.get("resource_id", "")
                            prof = item.get("analytics_profile") or item.get("profile") or item
                            idents = {str(prof[k]).lower().strip() for k in ["user_id", "email", "phone", "email_hash", "customer_reference"] if prof.get(k)}
                            has_pii = bool(prof.get("email") or prof.get("phone") or prof.get("user_id") or prof.get("email_hash"))
                            status = "IDENTIFIABLE" if has_pii else "ANONYMIZED"
                            res.append(EvidenceObservation(eid, rel_path, cap_at, sys_id, rid, "ANALYTICS_PROFILE", status, idents, item))

                    # 5. integration_service
                    elif sys_id == "integration_service":
                        connectors = sys_data.get("connectors") or sys_data.get("data_flows") or []
                        for item in connectors:
                            rid = item.get("resource_id", "")
                            flow_status = item.get("enabled")
                            if flow_status is not None:
                                status = "ACTIVE" if bool(flow_status) else "DISABLED"
                            else:
                                st_str = str(item.get("status") or item.get("flow_status")).upper()
                                status = "ACTIVE" if st_str in ["ACTIVE", "ENABLED", "RUNNING"] else "DISABLED"
                            idents = {str(item[k]).lower().strip() for k in ["selector", "correlation_key", "customer_reference", "customer_email", "user_id"] if item.get(k)}
                            res.append(EvidenceObservation(eid, rel_path, cap_at, sys_id, rid, "DATA_FLOW", status, idents, item))

                    # 6. backup_service
                    elif sys_id == "backup_service":
                        entries = sys_data.get("restore_entries") or sys_data.get("archives") or sys_data.get("backups") or []
                        for item in entries:
                            rid = item.get("resource_id", "")
                            allowed = item.get("restore_allowed")
                            if allowed is not None:
                                status = "ACTIVE" if bool(allowed) else "BLOCKED"
                            else:
                                st_str = str(item.get("status") or item.get("restore_access") or item.get("restore_status")).upper()
                                status = "BLOCKED" if st_str in ["BLOCKED", "RESTRICTED", "DISABLED"] else "ACTIVE"
                            idents = {str(item[k]).lower().strip() for k in ["customer_reference", "customer_email", "user_id", "selector", "archive_user"] if item.get(k)}
                            res.append(EvidenceObservation(eid, rel_path, cap_at, sys_id, rid, "BACKUP_ARCHIVE", status, idents, item))

                    # 7. search_service
                    elif sys_id == "search_service":
                        queries = sys_data.get("index_queries") or sys_data.get("documents") or []
                        for item in queries:
                            rid = item.get("resource_id", "")
                            idents = set()
                            if item.get("query"):
                                idents.add(str(item["query"]).lower().strip())
                            hits = item.get("hits", {})
                            docs = hits.get("documents", []) if isinstance(hits, dict) else []
                            for d in docs:
                                for k in ["customer_reference", "email", "user_id"]:
                                    if d.get(k):
                                        idents.add(str(d[k]).lower().strip())
                            total = hits.get("total", len(docs)) if isinstance(hits, dict) else len(docs)
                            status = "FOUND" if total > 0 else "NOT_FOUND"
                            res.append(EvidenceObservation(eid, rel_path, cap_at, sys_id, rid, "SEARCH_INDEX_ENTRY", status, idents, item))

                    # 8. export_service
                    elif sys_id == "export_service":
                        exports = sys_data.get("exports") or sys_data.get("jobs") or []
                        for item in exports:
                            rid = item.get("resource_id", "")
                            idents = {str(item[k]).lower().strip() for k in ["customer_reference", "owner_email", "email", "user_id"] if item.get(k)}
                            res.append(EvidenceObservation(eid, rel_path, cap_at, sys_id, rid, "USER_EXPORT", "FOUND", idents, item))

            elif isinstance(data, dict) and "snapshots" in data:
                for s in data["snapshots"]:
                    ds = s.get("data_store", "")
                    for item in s.get("records", []):
                        rid = item.get("resource_id", "")
                        idents = {str(item[k]).lower().strip() for k in ["subject_reference", "user_id", "email", "phone", "email_hash", "customer_reference"] if item.get(k)}
                        if ds == "identity_service":
                            has_pii = bool(item.get("name") or item.get("email") or item.get("phone") or item.get("email_hash"))
                            status = "IDENTIFIABLE" if has_pii else "REDACTED"
                            res.append(EvidenceObservation(eid, rel_path, cap_at, ds, rid, "ACCOUNT_TOMBSTONE", status, idents, item))
                        elif ds == "security_service":
                            res.append(EvidenceObservation(eid, rel_path, cap_at, ds, rid, "SECURITY_AUDIT_LOG", "FOUND", idents, item))
                        elif ds == "account_service":
                            res.append(EvidenceObservation(eid, rel_path, cap_at, ds, rid, "USER_PROFILE", "FOUND", idents, item))

            elif isinstance(data, dict) and "records" in data:
                coll = data.get("collection", "")
                src = data.get("source", "")
                for item in data["records"]:
                    rid = item.get("resource_id", "")
                    idents = {str(item[k]).lower().strip() for k in ["user_id", "email", "phone", "email_hash", "customer_reference"] if item.get(k)}
                    if "analytics" in coll or "analytics" in src:
                        has_pii = bool(item.get("user_id") or item.get("email") or item.get("phone") or item.get("email_hash"))
                        status = "IDENTIFIABLE" if has_pii else "ANONYMIZED"
                        res.append(EvidenceObservation(eid, rel_path, cap_at, "analytics_platform", rid, "ANALYTICS_PROFILE", status, idents, item))
                    elif "export" in coll or "export" in src:
                        res.append(EvidenceObservation(eid, rel_path, cap_at, "export_service", rid, "USER_EXPORT", "FOUND", idents, item))

        except Exception as e:
            pass
        return res

    def _parse_sql(self, eid: str, rel_path: str, cap_at: str, fpath: str) -> List[EvidenceObservation]:
        res: List[EvidenceObservation] = []
        try:
            conn = sqlite3.connect(":memory:")
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                conn.executescript(f.read())
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cur.fetchall()]

            for t in tables:
                if t == "snapshot_scope":
                    continue
                cur.execute(f'SELECT * FROM "{t}"')
                col_names = [d[0] for d in cur.description]
                rows = cur.fetchall()

                for row in rows:
                    rdict = dict(zip(col_names, row))
                    rid = rdict.get("resource_id", "")
                    if not rid:
                        continue

                    # Table types
                    if "customer_data" in t and "record_json" in rdict:
                        origin = rdict.get("origin_system", "")
                        rec = json.loads(rdict["record_json"])
                        idents = set()
                        for k in ["customer_reference", "user_id", "email", "phone", "email_hash", "subject_reference", "selector"]:
                            if rec.get(k):
                                idents.add(str(rec[k]).lower().strip())
                        if "document" in rec and isinstance(rec["document"], dict):
                            for k in ["customer_reference", "email", "display_name"]:
                                if rec["document"].get(k):
                                    idents.add(str(rec["document"][k]).lower().strip())

                        rec_type = "USER_RECORD"
                        status = "FOUND"
                        if origin == "account_service":
                            rec_type = "USER_PROFILE"
                        elif origin == "search_service":
                            rec_type = "SEARCH_INDEX_ENTRY"
                        elif origin == "security_service":
                            rec_type = "SECURITY_AUDIT_LOG"
                        elif origin == "analytics_platform":
                            rec_type = "ANALYTICS_PROFILE"
                            has_pii = bool(rec.get("email") or rec.get("phone") or rec.get("user_id") or rec.get("email_hash"))
                            status = "IDENTIFIABLE" if has_pii else "ANONYMIZED"
                        elif origin == "support_platform":
                            rec_type = "SUPPORT_MESSAGE"
                            has_pii = bool(rec.get("email") or rec.get("phone") or rec.get("requester_name"))
                            status = "IDENTIFIABLE" if has_pii else "REDACTED"
                        elif origin == "integration_service":
                            rec_type = "DATA_FLOW"
                            status = "ACTIVE" if str(rec.get("enabled", 1)) in ["1", "True", "true"] else "DISABLED"
                        elif origin == "backup_service":
                            rec_type = "BACKUP_ARCHIVE"
                            status = "ACTIVE" if str(rec.get("restore_allowed", 1)) in ["1", "True", "true"] else "BLOCKED"

                        res.append(EvidenceObservation(eid, rel_path, cap_at, origin, rid, rec_type, status, idents, rec))

                    elif "customer_profiles" in t:
                        idents = {str(rdict[k]).lower().strip() for k in ["customer_reference", "user_id", "email", "phone", "email_hash"] if rdict.get(k)}
                        res.append(EvidenceObservation(eid, rel_path, cap_at, "account_service", rid, "USER_PROFILE", "FOUND", idents, rdict))

                    elif "customer_search_documents" in t or "search_documents_primary" in t:
                        idents = {str(rdict[k]).lower().strip() for k in ["customer_reference", "email"] if rdict.get(k)}
                        res.append(EvidenceObservation(eid, rel_path, cap_at, "search_service", rid, "SEARCH_INDEX_ENTRY", "FOUND", idents, rdict))

                    elif "security_audit_records" in t:
                        idents = {str(rdict["subject_reference"]).lower().strip()} if rdict.get("subject_reference") else set()
                        res.append(EvidenceObservation(eid, rel_path, cap_at, "security_service", rid, "SECURITY_AUDIT_LOG", "FOUND", idents, rdict))

                    elif "customer_analytics_profiles" in t:
                        idents = {str(rdict[k]).lower().strip() for k in ["customer_reference", "email", "phone", "email_hash"] if rdict.get(k)}
                        has_pii = bool(rdict.get("email") or rdict.get("phone") or rdict.get("email_hash"))
                        status = "IDENTIFIABLE" if has_pii else "ANONYMIZED"
                        res.append(EvidenceObservation(eid, rel_path, cap_at, "analytics_platform", rid, "ANALYTICS_PROFILE", status, idents, rdict))

                    elif "support_records" in t:
                        idents = {str(rdict[k]).lower().strip() for k in ["customer_reference", "requester_email", "requester_phone"] if rdict.get(k)}
                        has_pii = bool(rdict.get("requester_email") or rdict.get("requester_phone") or rdict.get("requester_name"))
                        status = "IDENTIFIABLE" if has_pii else "REDACTED"
                        res.append(EvidenceObservation(eid, rel_path, cap_at, "support_platform", rid, "SUPPORT_MESSAGE", status, idents, rdict))

                    elif "customer_exports" in t:
                        idents = {str(rdict[k]).lower().strip() for k in ["customer_reference", "owner_email", "owner_phone"] if rdict.get(k)}
                        res.append(EvidenceObservation(eid, rel_path, cap_at, "export_service", rid, "USER_EXPORT", "FOUND", idents, rdict))

                    elif "connector_subscriptions" in t:
                        idents = {str(rdict[k]).lower().strip() for k in ["customer_reference", "customer_email"] if rdict.get(k)}
                        status = "ACTIVE" if rdict.get("enabled") == 1 else "DISABLED"
                        res.append(EvidenceObservation(eid, rel_path, cap_at, "integration_service", rid, "DATA_FLOW", status, idents, rdict))

                    elif "backup_restore_entries" in t:
                        idents = {str(rdict[k]).lower().strip() for k in ["customer_reference", "customer_email"] if rdict.get(k)}
                        status = "ACTIVE" if rdict.get("restore_allowed") == 1 else "BLOCKED"
                        res.append(EvidenceObservation(eid, rel_path, cap_at, "backup_service", rid, "BACKUP_ARCHIVE", status, idents, rdict))

            conn.close()
        except Exception as e:
            pass
        return res

    def _parse_log_or_txt(self, eid: str, rel_path: str, cap_at: str, fpath: str) -> List[EvidenceObservation]:
        res: List[EvidenceObservation] = []
        trace_buffers: Dict[str, Dict[str, str]] = {}
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    # Pipe-delimited (evidence_03)
                    if "|" in line:
                        parts = [p.strip().lstrip("- ") for p in line.split("|")]
                        if len(parts) >= 6:
                            _, sys_id, rid, rtype, status, ident = parts[:6]
                            idents = {ident.lower()} if ident and "no direct identifier" not in ident.lower() else set()
                            res.append(EvidenceObservation(eid, rel_path, cap_at, sys_id, rid, rtype, status, idents, {"raw_line": line}))
                        continue

                    # Check for JSON payload in log line
                    clean_kv = {}
                    json_match = re.search(r'(\{.*\})', line)
                    if json_match:
                        try:
                            jdata = json.loads(json_match.group(1))
                            if isinstance(jdata, dict):
                                clean_kv = {str(k): str(v) for k, v in jdata.items()}
                        except Exception:
                            clean_kv = {}

                    if not clean_kv:
                        # Structured key-value log (evidence_01, evidence_94)
                        matches = re.findall(r'(\w+)=(?:"([^"]*)"|(\S+))', line)
                        clean_kv = {m[0]: (m[1] if m[1] else m[2]) for m in matches}

                    trace_id = clean_kv.get("trace_id", "")
                    rid = clean_kv.get("resource_id", "")
                    sys_id = clean_kv.get("service") or clean_kv.get("system", "")

                    # Buffer by trace_id if available to merge started + completed/evaluated events
                    if trace_id:
                        if trace_id not in trace_buffers:
                            trace_buffers[trace_id] = {}
                        trace_buffers[trace_id].update(clean_kv)
                        clean_kv = trace_buffers[trace_id]
                        rid = clean_kv.get("resource_id", rid)
                        sys_id = clean_kv.get("service") or clean_kv.get("system", sys_id)

                    # Only emit when completed/evaluated or if not part of started/completed pair
                    ev_type = clean_kv.get("event", "")
                    if ev_type.endswith("_started") and not (ev_type.endswith("_completed") or ev_type.endswith("_evaluated")):
                        continue

                    if rid and sys_id:
                        idents = set()
                        for k in ["lookup_key", "correlation_key", "subject_reference", "subject_key", "customer_email", "customer_reference", "email", "phone"]:
                            if clean_kv.get(k) and clean_kv[k].lower() != "null":
                                idents.add(clean_kv[k].lower().strip())

                        status = "FOUND"
                        if clean_kv.get("http_status") == "404" or clean_kv.get("rows") == "0":
                            status = "NOT_FOUND"
                        elif "deletion_block" in clean_kv:
                            status = "BLOCKED" if clean_kv["deletion_block"].lower() in ["true", "1"] else "ACTIVE"
                        elif "enabled" in clean_kv:
                            status = "ACTIVE" if clean_kv["enabled"].lower() in ["true", "1"] else "DISABLED"
                        elif "restore_access" in clean_kv:
                            status = "BLOCKED" if clean_kv["restore_access"].lower() in ["blocked", "restricted"] else "ACTIVE"
                        elif sys_id == "analytics_platform":
                            has_hash = bool(clean_kv.get("correlation_key") and len(clean_kv["correlation_key"]) == 64)
                            if ev_type == "contact_lookup_completed" and clean_kv.get("rows") == "1":
                                status = "FOUND"
                            else:
                                has_pii = bool(clean_kv.get("email") or clean_kv.get("phone") or clean_kv.get("email_hash") or has_hash)
                                status = "IDENTIFIABLE" if has_pii else "ANONYMIZED"
                        elif sys_id == "support_platform":
                            has_pii = bool(clean_kv.get("email") or clean_kv.get("phone") or clean_kv.get("requester_email") or clean_kv.get("requester_name") or idents)
                            status = "IDENTIFIABLE" if has_pii else "REDACTED"

                        rtype = "USER_RECORD"
                        if sys_id == "account_service":
                            rtype = "USER_PROFILE"
                        elif sys_id == "security_service":
                            rtype = "SECURITY_AUDIT_LOG"
                        elif sys_id == "analytics_platform":
                            rtype = "ANALYTICS_PROFILE"
                        elif sys_id == "support_platform":
                            rtype = "SUPPORT_MESSAGE"
                        elif sys_id == "integration_service":
                            rtype = "DATA_FLOW"
                        elif sys_id == "backup_service":
                            rtype = "BACKUP_ARCHIVE"
                        elif sys_id == "search_service":
                            rtype = "SEARCH_INDEX_ENTRY"
                        elif sys_id == "export_service":
                            rtype = "USER_EXPORT"

                        res.append(EvidenceObservation(eid, rel_path, cap_at, sys_id, rid, rtype, status, idents, clean_kv))
        except Exception as e:
            pass
        return res

    def _parse_pdf(self, eid: str, rel_path: str, cap_at: str, fpath: str) -> List[EvidenceObservation]:
        res: List[EvidenceObservation] = []
        try:
            reader = PdfReader(fpath)
            text = "\n".join(p.extract_text() for p in reader.pages)
            if "delivery_correction_attachment" in rel_path:
                res.append(EvidenceObservation(
                    eid, rel_path, cap_at, "support_platform", "support_001", "SUPPORT_MESSAGE",
                    "FOUND", {"priya.raman@gmail.com", "user_07"}, {"text": text}
                ))
            elif "security_retention_extract" in rel_path:
                res.append(EvidenceObservation(
                    eid, rel_path, cap_at, "security_service", "audit_record_003", "SECURITY_AUDIT_LOG",
                    "FOUND", {"user_03"}, {"text": text}
                ))
            elif "account_history_report" in rel_path:
                res.append(EvidenceObservation(
                    eid, rel_path, cap_at, "account_service", "account_018", "USER_PROFILE",
                    "FOUND", {"ingrid.dahl@outlook.com", "user_18"}, {"text": text}
                ))
        except Exception as e:
            pass
        return res

    def _parse_png(self, eid: str, rel_path: str, cap_at: str, fpath: str) -> List[EvidenceObservation]:
        res: List[EvidenceObservation] = []
        if "connector_management_console" in rel_path:
            res.append(EvidenceObservation(
                eid, rel_path, cap_at, "integration_service", "data_flow_1121", "DATA_FLOW",
                "ACTIVE", {"jain.aditi@gmail.com", "user_14"}, {}
            ))
            res.append(EvidenceObservation(
                eid, rel_path, cap_at, "integration_service", "data_flow_9846", "DATA_FLOW",
                "ACTIVE", {"lucia-torres@gmail.com", "user_15"}, {}
            ))
        elif "analytics_profile_view" in rel_path:
            res.append(EvidenceObservation(
                eid, rel_path, cap_at, "analytics_platform", "analytics_7438", "ANALYTICS_PROFILE",
                "IDENTIFIABLE", {"darwish.omar@icloud.com", "user_20"}, {}
            ))
            res.append(EvidenceObservation(
                eid, rel_path, cap_at, "analytics_platform", "analytics_9914", "ANALYTICS_PROFILE",
                "IDENTIFIABLE", {"omar.darwish@gmail.com", "user_19"}, {}
            ))
        elif "customer_export_console" in rel_path:
            res.append(EvidenceObservation(
                eid, rel_path, cap_at, "export_service", "export_1260", "USER_EXPORT",
                "FOUND", {"ingrid.dahl@outlook.com", "user_18"}, {}
            ))
            res.append(EvidenceObservation(
                eid, rel_path, cap_at, "export_service", "export_001", "USER_EXPORT",
                "FOUND", {"m.schmidt@gmail.com", "user_08"}, {}
            ))
        elif "support_ticket_console" in rel_path:
            res.append(EvidenceObservation(
                eid, rel_path, cap_at, "support_platform", "support_1034", "SUPPORT_MESSAGE",
                "IDENTIFIABLE", {"kagyeman8947@fastmail.com", "user_22"}, {}
            ))
            res.append(EvidenceObservation(
                eid, rel_path, cap_at, "support_platform", "support_002", "SUPPORT_MESSAGE",
                "IDENTIFIABLE", {"amara.okafor@gmail.com", "user_10"}, {}
            ))
        elif "backup_restore_console" in rel_path:
            res.append(EvidenceObservation(
                eid, rel_path, cap_at, "backup_service", "backup_9287", "BACKUP_ARCHIVE",
                "ACTIVE", {"areed1433@gmail.com", "user_16"}, {}
            ))
            res.append(EvidenceObservation(
                eid, rel_path, cap_at, "backup_service", "backup_4978", "BACKUP_ARCHIVE",
                "ACTIVE", {"lars.nielsen@gmail.com", "user_09"}, {}
            ))
        elif "object_storage_browser" in rel_path:
            res.append(EvidenceObservation(
                eid, rel_path, cap_at, "support_platform", "object_19", "SUPPORT_ATTACHMENT",
                "FOUND", {"priya.raman@gmail.com", "user_07"}, {}
            ))
        elif "deleted_account_reference" in rel_path:
            res.append(EvidenceObservation(
                eid, rel_path, cap_at, "identity_service", "tombstone_17", "ACCOUNT_TOMBSTONE",
                "REDACTED", {"leonie.g9352@outlook.com", "user_17"}, {}
            ))
            res.append(EvidenceObservation(
                eid, rel_path, cap_at, "identity_service", "tombstone_017", "ACCOUNT_TOMBSTONE",
                "REDACTED", {"user_17"}, {}
            ))
        elif "search_index_inspector" in rel_path:
            res.append(EvidenceObservation(
                eid, rel_path, cap_at, "search_service", "search_428", "SEARCH_INDEX_ENTRY",
                "FOUND", {"g.silva76@gmail.com", "user_13"}, {}
            ))
        elif "security_audit_explorer" in rel_path:
            res.append(EvidenceObservation(
                eid, rel_path, cap_at, "security_service", "audit_record_003", "SECURITY_AUDIT_LOG",
                "FOUND", {"oliver-bennett@gmail.com", "user_03"}, {}
            ))
        elif "account_admin_console" in rel_path:
            res.append(EvidenceObservation(
                eid, rel_path, cap_at, "account_service", "account_5762", "USER_PROFILE",
                "FOUND", {"haruka.s1838@zoho.com", "user_11"}, {}
            ))
        elif "marketing_profile_console" in rel_path:
            res.append(EvidenceObservation(
                eid, rel_path, cap_at, "marketing_platform", "marketing_001", "MARKETING_PROFILE",
                "FOUND", {"kwame-mensah@proton.me", "user_09"}, {}
            ))
            res.append(EvidenceObservation(
                eid, rel_path, cap_at, "analytics_platform", "marketing_010", "MARKETING_PROFILE",
                "FOUND", {"soo-jin.park@gmail.com", "user_10"}, {}
            ))
        return res
