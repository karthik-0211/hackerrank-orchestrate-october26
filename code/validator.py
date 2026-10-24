"""Independent Submission Output Validator.

Strictly validates generated output.csv against all challenge requirements:
- Exact columns: case_id,deletion_status,steps_json
- Exactly 518 data rows (or specified expected count)
- Unique and consecutively sorted case_id
- Allowed status enums: COMPLETE, INCOMPLETE, NOT_APPLICABLE
- NOT_APPLICABLE steps_json == []
- Valid JSON array with exactly the 7 required keys
- Consecutive step_no starting at 1
- Strict phase, operation, and state legality
- Phase and operation order compliance
- Non-empty evidence_id for findings and COMPLETE verifications
- Empty evidence_id for proposed remediation and future verifications
"""

from __future__ import annotations

import csv
import json
import os
import re
from typing import Any, Dict, List, Set, Tuple

LEGAL_COMBINATIONS = {
    # Phase: FINDING
    ("FINDING", "REPORT_REMAINING_RECORD", "PRESENT"),
    ("FINDING", "REPORT_EXPOSED_PII", "PRESENT"),
    ("FINDING", "REPORT_ACTIVE_DATA_FLOW", "ACTIVE"),
    ("FINDING", "REPORT_RESTORE_RISK", "ACTIVE"),

    # Phase: REMEDIATION
    ("REMEDIATION", "DISABLE_DATA_FLOW", "DISABLED"),
    ("REMEDIATION", "BLOCK_RESTORE", "BLOCKED"),
    ("REMEDIATION", "DELETE_RECORD", "ABSENT"),
    ("REMEDIATION", "REDACT_RECORD", "REDACTED"),
    ("REMEDIATION", "ANONYMIZE_RECORD", "ANONYMIZED"),

    # Phase: VERIFICATION
    ("VERIFICATION", "VERIFY_RECORD_ABSENT", "ABSENT"),
    ("VERIFICATION", "VERIFY_RECORD_PRESENT", "PRESENT"),
    ("VERIFICATION", "VERIFY_RECORD_REDACTED", "REDACTED"),
    ("VERIFICATION", "VERIFY_RECORD_ANONYMIZED", "ANONYMIZED"),
    ("VERIFICATION", "VERIFY_DATA_FLOW_DISABLED", "DISABLED"),
    ("VERIFICATION", "VERIFY_RESTORE_BLOCKED", "BLOCKED"),
}

REQUIRED_STEP_KEYS = {
    "step_no",
    "phase",
    "system_id",
    "resource_id",
    "operation",
    "state",
    "evidence_id",
}

PHASE_ORDER = {"FINDING": 1, "REMEDIATION": 2, "VERIFICATION": 3}

OPERATION_ORDER = {
    "REPORT_REMAINING_RECORD": 1,
    "REPORT_EXPOSED_PII": 2,
    "REPORT_ACTIVE_DATA_FLOW": 3,
    "REPORT_RESTORE_RISK": 4,
    "DISABLE_DATA_FLOW": 1,
    "BLOCK_RESTORE": 2,
    "DELETE_RECORD": 3,
    "REDACT_RECORD": 4,
    "ANONYMIZE_RECORD": 5,
    "VERIFY_RECORD_ABSENT": 1,
    "VERIFY_RECORD_PRESENT": 2,
    "VERIFY_RECORD_REDACTED": 3,
    "VERIFY_RECORD_ANONYMIZED": 4,
    "VERIFY_DATA_FLOW_DISABLED": 5,
    "VERIFY_RESTORE_BLOCKED": 6,
}


def case_num(cid: str) -> int:
    m = re.search(r"\d+", cid)
    return int(m.group(0)) if m else 0


class OutputValidator:
    def __init__(self, valid_evidence_ids: Optional[Set[str]] = None):
        self.valid_evidence_ids = valid_evidence_ids or set()

    def validate_file(self, csv_path: str, expected_count: Optional[int] = 518) -> List[str]:
        errors: List[str] = []
        if not os.path.exists(csv_path):
            return [f"File not found: {csv_path}"]

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if header != ["case_id", "deletion_status", "steps_json"]:
                errors.append(f"Invalid header: {header}. Expected: ['case_id', 'deletion_status', 'steps_json']")

            rows = list(reader)

        if expected_count is not None and len(rows) != expected_count:
            errors.append(f"Expected {expected_count} rows, found {len(rows)}")

        seen_cases: Set[str] = set()
        prev_case_num = -1

        for idx, row in enumerate(rows, start=1):
            if len(row) != 3:
                errors.append(f"Row {idx} has {len(row)} columns, expected 3")
                continue

            cid, status, steps_raw = row

            # Case uniqueness and sorting
            if cid in seen_cases:
                errors.append(f"Duplicate case_id: {cid}")
            seen_cases.add(cid)

            c_num = case_num(cid)
            if c_num < prev_case_num:
                errors.append(f"Unsorted case_id: {cid} after case {prev_case_num}")
            prev_case_num = c_num

            # Status enum
            if status not in ["COMPLETE", "INCOMPLETE", "NOT_APPLICABLE"]:
                errors.append(f"Row {idx} ({cid}): Invalid status '{status}'")

            # Parse steps JSON
            try:
                steps = json.loads(steps_raw)
            except Exception as e:
                errors.append(f"Row {idx} ({cid}): steps_json is not valid JSON: {e}")
                continue

            if not isinstance(steps, list):
                errors.append(f"Row {idx} ({cid}): steps_json is not a JSON array")
                continue

            # NOT_APPLICABLE contract
            if status == "NOT_APPLICABLE":
                if steps != []:
                    errors.append(f"Row {idx} ({cid}): NOT_APPLICABLE must have steps_json = [], found {len(steps)} steps")
                continue

            # COMPLETE contract
            if status == "COMPLETE":
                for s in steps:
                    if s.get("phase") != "VERIFICATION":
                        errors.append(f"Row {idx} ({cid}): COMPLETE status cannot have phase '{s.get('phase')}'")
                    if not s.get("evidence_id"):
                        errors.append(f"Row {idx} ({cid}): COMPLETE status verification must cite non-empty evidence_id")

            # INCOMPLETE contract
            if status == "INCOMPLETE":
                phases = {s.get("phase") for s in steps}
                if "FINDING" not in phases or "REMEDIATION" not in phases or "VERIFICATION" not in phases:
                    errors.append(f"Row {idx} ({cid}): INCOMPLETE must contain FINDING, REMEDIATION, and VERIFICATION phases")

            # Step level validation
            prev_p_ord = -1
            prev_op_ord = -1
            prev_sys = ""
            prev_res = ""

            for step_i, step in enumerate(steps, start=1):
                # 7 required keys
                if set(step.keys()) != REQUIRED_STEP_KEYS:
                    errors.append(f"Row {idx} ({cid}) Step {step_i}: Invalid keys {set(step.keys())}")

                # Consecutive step_no
                if step.get("step_no") != step_i:
                    errors.append(f"Row {idx} ({cid}) Step {step_i}: step_no is {step.get('step_no')}, expected {step_i}")

                phase = step.get("phase", "")
                op = step.get("operation", "")
                st = step.get("state", "")
                ev_id = step.get("evidence_id", "")
                sys_id = step.get("system_id", "")
                res_id = step.get("resource_id", "")

                # Legal enum combination
                if (phase, op, st) not in LEGAL_COMBINATIONS:
                    errors.append(f"Row {idx} ({cid}) Step {step_i}: Illegal combination ({phase}, {op}, {st})")

                # Evidence ID rules
                if phase == "FINDING" and not ev_id:
                    errors.append(f"Row {idx} ({cid}) Step {step_i}: FINDING must have non-empty evidence_id")
                if phase == "REMEDIATION" and ev_id != "":
                    errors.append(f"Row {idx} ({cid}) Step {step_i}: REMEDIATION must have empty evidence_id, found '{ev_id}'")
                if phase == "VERIFICATION" and status == "INCOMPLETE" and ev_id != "":
                    errors.append(f"Row {idx} ({cid}) Step {step_i}: INCOMPLETE future VERIFICATION must have empty evidence_id, found '{ev_id}'")

                if ev_id and self.valid_evidence_ids and ev_id not in self.valid_evidence_ids:
                    errors.append(f"Row {idx} ({cid}) Step {step_i}: Unknown evidence_id '{ev_id}'")

                # Ordering validation
                p_ord = PHASE_ORDER.get(phase, 99)
                op_ord = OPERATION_ORDER.get(op, 99)

                curr_sort = (p_ord, op_ord, sys_id, res_id)
                prev_sort = (prev_p_ord, prev_op_ord, prev_sys, prev_res)
                if curr_sort < prev_sort:
                    errors.append(f"Row {idx} ({cid}) Step {step_i}: Step out of order. Current: {curr_sort}, Previous: {prev_sort}")

                prev_p_ord, prev_op_ord, prev_sys, prev_res = curr_sort

        return errors
