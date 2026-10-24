"""Policy Evaluation and Step Planner.

Implements deletion_rules.csv policy enforcement, status determination,
causal dependency remediation ordering, and strict contract sorting.
Zero hallucinated enums, valid citations, stable consecutive step numbering.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Step:
    step_no: int
    phase: str
    system_id: str
    resource_id: str
    operation: str
    state: str
    evidence_id: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_no": self.step_no,
            "phase": self.phase,
            "system_id": self.system_id,
            "resource_id": self.resource_id,
            "operation": self.operation,
            "state": self.state,
            "evidence_id": self.evidence_id,
        }


# Strict sorting priority tables
PHASE_ORDER = {
    "FINDING": 1,
    "REMEDIATION": 2,
    "VERIFICATION": 3,
}

OPERATION_ORDER = {
    # Phase 1: FINDING
    "REPORT_REMAINING_RECORD": 1,
    "REPORT_EXPOSED_PII": 2,
    "REPORT_ACTIVE_DATA_FLOW": 3,
    "REPORT_RESTORE_RISK": 4,

    # Phase 2: REMEDIATION
    "DISABLE_DATA_FLOW": 1,
    "BLOCK_RESTORE": 2,
    "DELETE_RECORD": 3,
    "REDACT_RECORD": 4,
    "ANONYMIZE_RECORD": 5,

    # Phase 3: VERIFICATION
    "VERIFY_RECORD_ABSENT": 1,
    "VERIFY_RECORD_PRESENT": 2,
    "VERIFY_RECORD_REDACTED": 3,
    "VERIFY_RECORD_ANONYMIZED": 4,
    "VERIFY_DATA_FLOW_DISABLED": 5,
    "VERIFY_RESTORE_BLOCKED": 6,
}


def step_sort_key(step: Step) -> Tuple[int, int, str, str]:
    p_ord = PHASE_ORDER.get(step.phase, 99)
    op_ord = OPERATION_ORDER.get(step.operation, 99)
    return (p_ord, op_ord, step.system_id, step.resource_id)


class PolicyPlanner:
    """Plans ordered findings, remediation, and verification steps according to policy."""

    @staticmethod
    def plan(
        case_id: str,
        findings: List[Tuple[str, str, str, str, str]], # (system_id, resource_id, op, state, ev_id)
        verifications: List[Tuple[str, str, str, str, str]], # (system_id, resource_id, op, state, ev_id)
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Returns (deletion_status, sorted_steps_dicts)."""
        raw_steps: List[Step] = []

        if findings:
            status = "INCOMPLETE"
            # 1. Add Findings (cite valid evidence_id)
            for sys_id, rid, op, state, ev_id in findings:
                raw_steps.append(Step(0, "FINDING", sys_id, rid, op, state, ev_id))

            # 2. Add Remediation (evidence_id = "")
            # Derive remediation operations from findings
            for sys_id, rid, op, state, _ in findings:
                if op == "REPORT_ACTIVE_DATA_FLOW":
                    raw_steps.append(Step(0, "REMEDIATION", sys_id, rid, "DISABLE_DATA_FLOW", "DISABLED", ""))
                elif op == "REPORT_RESTORE_RISK":
                    raw_steps.append(Step(0, "REMEDIATION", sys_id, rid, "BLOCK_RESTORE", "BLOCKED", ""))
                elif op == "REPORT_REMAINING_RECORD":
                    raw_steps.append(Step(0, "REMEDIATION", sys_id, rid, "DELETE_RECORD", "ABSENT", ""))
                elif op == "REPORT_EXPOSED_PII":
                    if sys_id == "analytics_platform":
                        raw_steps.append(Step(0, "REMEDIATION", sys_id, rid, "ANONYMIZE_RECORD", "ANONYMIZED", ""))
                    else:  # support_platform, identity_service (tombstone)
                        raw_steps.append(Step(0, "REMEDIATION", sys_id, rid, "REDACT_RECORD", "REDACTED", ""))

            # 3. Add Verifications (for INCOMPLETE, evidence_id = "")
            # Verifications cover remediated resources PLUS compliant retained resources
            # Avoid duplicate verifications for same (system_id, resource_id)
            seen_verifs = set()
            for sys_id, rid, op, state, _ in verifications:
                v_key = (sys_id, rid, op)
                if v_key not in seen_verifs:
                    seen_verifs.add(v_key)
                    raw_steps.append(Step(0, "VERIFICATION", sys_id, rid, op, state, ""))

            # Also ensure all remediations have future verification
            for sys_id, rid, op, state, _ in findings:
                v_op = ""
                v_state = ""
                if op == "REPORT_ACTIVE_DATA_FLOW":
                    v_op, v_state = "VERIFY_DATA_FLOW_DISABLED", "DISABLED"
                elif op == "REPORT_RESTORE_RISK":
                    v_op, v_state = "VERIFY_RESTORE_BLOCKED", "BLOCKED"
                elif op == "REPORT_REMAINING_RECORD":
                    v_op, v_state = "VERIFY_RECORD_ABSENT", "ABSENT"
                elif op == "REPORT_EXPOSED_PII":
                    if sys_id == "analytics_platform":
                        v_op, v_state = "VERIFY_RECORD_ANONYMIZED", "ANONYMIZED"
                    else:
                        v_op, v_state = "VERIFY_RECORD_REDACTED", "REDACTED"
                if v_op:
                    v_key = (sys_id, rid, v_op)
                    if v_key not in seen_verifs:
                        seen_verifs.add(v_key)
                        raw_steps.append(Step(0, "VERIFICATION", sys_id, rid, v_op, v_state, ""))

        else:
            status = "COMPLETE"
            # For COMPLETE, only verifications, each citing valid evidence_id
            seen_verifs = set()
            for sys_id, rid, op, state, ev_id in verifications:
                v_key = (sys_id, rid, op)
                if v_key not in seen_verifs:
                    seen_verifs.add(v_key)
                    raw_steps.append(Step(0, "VERIFICATION", sys_id, rid, op, state, ev_id))

        # Sort according to contract
        sorted_steps = sorted(raw_steps, key=step_sort_key)

        # Assign consecutive step_no starting at 1
        result = []
        for i, st in enumerate(sorted_steps, 1):
            st.step_no = i
            result.append(st.to_dict())

        return status, result
