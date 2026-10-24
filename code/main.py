"""Main entry point for the Evidence-First AI Deletion Audit Agent.

Generates the root-level output.csv for dataset/deletion_requests.csv.
Adheres strictly to the HackerRank Orchestrate October 2026 contract:
- Header: case_id,deletion_status,steps_json
- Exactly 518 data rows sorted by case_id
- Strict phase, operation, and state legality
"""

import csv
import json
import os
import sys
from typing import Any, Dict, List

# Ensure repository root is on sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from code.state_reconstructor import StateReconstructor
from code.validator import OutputValidator, case_num


def main() -> None:
    dataset_dir = os.path.join(REPO_ROOT, "dataset")
    input_file = os.path.join(dataset_dir, "deletion_requests.csv")
    output_file = os.path.join(REPO_ROOT, "output.csv")

    print("[*] Starting Ghost Data Deletion Audit Agent")
    print(f"[*] Repository root: {REPO_ROOT}")
    print(f"[*] Loading input requests from: {input_file}")

    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")

    with open(input_file, "r", encoding="utf-8") as f:
        requests = list(csv.DictReader(f))

    print(f"[*] Total requests to process: {len(requests)}")

    # Initialize state reconstructor (indexes evidence, activity, identities)
    print("[*] Initializing evidence index and state reconstructor...")
    reconstructor = StateReconstructor(dataset_dir)
    print(f"[*] Evidence indexing complete. {len(reconstructor.indexer.observations)} observations indexed.")

    results: List[Dict[str, Any]] = []

    for idx, req in enumerate(requests, 1):
        cid = req["case_id"]
        status, steps = reconstructor.audit_case(req)
        steps_json = json.dumps(steps, separators=(",", ":"))
        results.append({
            "case_id": cid,
            "deletion_status": status,
            "steps_json": steps_json,
        })
        if idx % 100 == 0 or idx == len(requests):
            print(f"[*] Processed {idx}/{len(requests)} cases...")

    # Sort results strictly by numeric case_id
    results.sort(key=lambda r: case_num(r["case_id"]))

    print(f"[*] Writing {len(results)} rows to {output_file}...")
    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["case_id", "deletion_status", "steps_json"])
        for r in results:
            writer.writerow([r["case_id"], r["deletion_status"], r["steps_json"]])

    print("[*] Validating generated output.csv against challenge contract...")
    validator = OutputValidator()
    errors = validator.validate_file(output_file, expected_count=len(requests))

    if errors:
        print(f"[!] Validation failed with {len(errors)} errors:")
        for err in errors[:10]:
            print(f"    - {err}")
        sys.exit(1)
    else:
        print(f"[+] Output validation PASSED! Exactly {len(results)} rows valid and sorted.")


if __name__ == "__main__":
    main()
