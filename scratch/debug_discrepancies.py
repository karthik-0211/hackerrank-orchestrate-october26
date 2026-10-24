import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from code.evaluation.main import run_evaluation, normalize_step
import csv
import json

res = run_evaluation()

dataset_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset")
sample_out_path = os.path.join(dataset_dir, "sample_output.csv")
sample_expected = {r["case_id"]: r for r in csv.DictReader(open(sample_out_path, encoding='utf-8'))}

from code.state_reconstructor import StateReconstructor
reconstructor = StateReconstructor(dataset_dir)
sample_requests = list(csv.DictReader(open(os.path.join(dataset_dir, "sample_deletion_requests.csv"), encoding='utf-8')))

print("\n" + "="*80)
print("DETAILED DISCREPANCIES:")
print("="*80)

for req in sample_requests:
    cid = req["case_id"]
    exp_row = sample_expected[cid]
    exp_status = exp_row["deletion_status"]
    exp_steps = json.loads(exp_row["steps_json"])
    pred_status, pred_steps = reconstructor.audit_case(req)

    exp_norm = [normalize_step(s) for s in exp_steps]
    pred_norm = [normalize_step(s) for s in pred_steps]

    if pred_status != exp_status or exp_norm != pred_norm:
        print(f"\n[{cid}] Status: Pred={pred_status} | Exp={exp_status}")
        print("  Missing expected steps:")
        for s in exp_norm:
            if s not in pred_norm:
                print(f"    - EXP: {s}")
        print("  Unexpected predicted steps:")
        for s in pred_norm:
            if s not in exp_norm:
                print(f"    + PRED: {s}")
