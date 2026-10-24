"""Evaluation Pipeline.

Runs automated verification against:
1. Public sample reference (dataset/sample_deletion_requests.csv vs dataset/sample_output.csv)
2. Team-created synthetic evaluation cases (testing edge cases)
Computes case-level status accuracy, step-level precision/recall, operation correctness, and sequence accuracy.
"""

from __future__ import annotations

import csv
import json
import os
import sys
from typing import Any, Dict, List, Set, Tuple

# Add repo root to path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)

from code.state_reconstructor import StateReconstructor
from code.validator import OutputValidator


def normalize_step(s: Dict[str, Any]) -> Tuple[str, str, str, str, str, str]:
    """Tuple for comparison: (phase, system_id, resource_id, operation, state, evidence_id)."""
    return (
        s.get("phase", ""),
        s.get("system_id", ""),
        s.get("resource_id", ""),
        s.get("operation", ""),
        s.get("state", ""),
        s.get("evidence_id", ""),
    )


def run_evaluation() -> Dict[str, Any]:
    dataset_dir = os.path.join(REPO_ROOT, "dataset")
    reconstructor = StateReconstructor(dataset_dir)

    # 1. Public sample evaluation
    sample_req_path = os.path.join(dataset_dir, "sample_deletion_requests.csv")
    sample_out_path = os.path.join(dataset_dir, "sample_output.csv")

    with open(sample_req_path, "r", encoding="utf-8") as f:
        sample_requests = list(csv.DictReader(f))

    with open(sample_out_path, "r", encoding="utf-8") as f:
        sample_expected = {r["case_id"]: r for r in csv.DictReader(f)}

    print(f"=== PUBLIC SAMPLE EVALUATION ({len(sample_requests)} cases) ===")
    status_correct = 0
    total_expected_steps = 0
    total_predicted_steps = 0
    exact_matched_steps = 0
    exact_sequence_matches = 0
    case_results = []

    for req in sample_requests:
        cid = req["case_id"]
        exp_row = sample_expected[cid]
        exp_status = exp_row["deletion_status"]
        exp_steps = json.loads(exp_row["steps_json"])

        pred_status, pred_steps = reconstructor.audit_case(req)

        # Check status
        st_match = (pred_status == exp_status)
        if st_match:
            status_correct += 1

        # Check steps
        exp_norm = [normalize_step(s) for s in exp_steps]
        pred_norm = [normalize_step(s) for s in pred_steps]

        total_expected_steps += len(exp_norm)
        total_predicted_steps += len(pred_norm)

        # Matched steps
        matched_in_case = 0
        exp_set = set(exp_norm)
        for ps in pred_norm:
            if ps in exp_set:
                matched_in_case += 1
        exact_matched_steps += matched_in_case

        # Sequence match
        seq_match = (exp_norm == pred_norm)
        if seq_match:
            exact_sequence_matches += 1

        case_results.append({
            "case_id": cid,
            "status_match": st_match,
            "pred_status": pred_status,
            "exp_status": exp_status,
            "seq_match": seq_match,
            "pred_step_count": len(pred_steps),
            "exp_step_count": len(exp_steps),
        })

    status_acc = status_correct / len(sample_requests) if sample_requests else 0.0
    step_precision = exact_matched_steps / total_predicted_steps if total_predicted_steps else 0.0
    step_recall = exact_matched_steps / total_expected_steps if total_expected_steps else 0.0
    step_f1 = (2 * step_precision * step_recall / (step_precision + step_recall)) if (step_precision + step_recall) else 0.0
    seq_acc = exact_sequence_matches / len(sample_requests) if sample_requests else 0.0

    print(f"Status Accuracy: {status_correct}/{len(sample_requests)} ({status_acc:.2%})")
    print(f"Step Precision:  {exact_matched_steps}/{total_predicted_steps} ({step_precision:.2%})")
    print(f"Step Recall:     {exact_matched_steps}/{total_expected_steps} ({step_recall:.2%})")
    print(f"Step F1:         {step_f1:.2%}")
    print(f"Sequence Acc:    {exact_sequence_matches}/{len(sample_requests)} ({seq_acc:.2%})")

    # 2. Team-Created Synthetic Evaluation Cases
    print("\n=== SYNTHETIC EDGE-CASE EVALUATION ===")
    synthetic_cases = [
        {
            "case_id": "synth_01_non_del",
            "email": "test.export@example.com",
            "requested_at": "2026-09-01T10:00:00Z",
            "reported_status": "COMPLETE",
            "reported_at": "2026-09-02T10:00:00Z",
            "audit_at": "2026-09-15T12:00:00Z",
            "request_text": "I need to download my account data in portable format. Please do not close or delete my account.",
            "expected_status": "NOT_APPLICABLE",
            "expected_steps_count": 0,
        },
        {
            "case_id": "synth_02_historical_alias",
            "email": "minjun.kim90@gmail.com",
            "requested_at": "2026-08-20T10:00:00Z",
            "reported_status": "COMPLETE",
            "reported_at": "2026-08-25T12:00:00Z",
            "audit_at": "2026-09-15T12:00:00Z",
            "request_text": "Please delete all records and account details permanently.",
            "expected_status": "INCOMPLETE",  # user_12 has remaining analytics_9914
            "expected_min_steps": 3,
        },
        {
            "case_id": "synth_03_exposed_tombstone",
            "email": "addo.kofi@gmail.com",
            "requested_at": "2026-09-01T10:00:00Z",
            "reported_status": "COMPLETE",
            "reported_at": "2026-09-06T12:00:00Z",
            "audit_at": "2026-09-15T12:00:00Z",
            "request_text": "Please erase my account and purge personal data.",
            "expected_status": "INCOMPLETE",  # tombstone has exposed name, email, phone
            "expected_min_steps": 3,
        },
    ]

    synthetic_passed = 0
    for sc in synthetic_cases:
        p_stat, p_steps = reconstructor.audit_case(sc)
        passed = (p_stat == sc["expected_status"])
        if "expected_steps_count" in sc:
            passed = passed and (len(p_steps) == sc["expected_steps_count"])
        if "expected_min_steps" in sc:
            passed = passed and (len(p_steps) >= sc["expected_min_steps"])

        if passed:
            synthetic_passed += 1
            print(f"  PASS: {sc['case_id']} -> {p_stat} (steps: {len(p_steps)})")
        else:
            print(f"  FAIL: {sc['case_id']} -> got {p_stat} (steps: {len(p_steps)}), expected {sc['expected_status']}")

    print(f"Synthetic Tests Passed: {synthetic_passed}/{len(synthetic_cases)}")

    return {
        "status_accuracy": status_acc,
        "step_precision": step_precision,
        "step_recall": step_recall,
        "step_f1": step_f1,
        "sequence_accuracy": seq_acc,
        "status_correct": status_correct,
        "total_cases": len(sample_requests),
        "synthetic_passed": synthetic_passed,
        "total_synthetic": len(synthetic_cases),
        "case_results": case_results,
    }


if __name__ == "__main__":
    run_evaluation()
