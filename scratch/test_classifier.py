import csv
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import directly from code directory to avoid standard library code module conflict
import importlib.util
spec = importlib.util.spec_from_file_location("classifier", os.path.join(os.path.dirname(os.path.abspath(__file__)), "code", "classifier.py"))
classifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(classifier)
RequestClassifier = classifier.RequestClassifier

samples = list(csv.DictReader(open('dataset/sample_deletion_requests.csv', encoding='utf-8')))
print('Testing 32 sample requests:')
for s in samples:
    is_del, reason = RequestClassifier.classify(s['request_text'])
    if not is_del:
        print(f"  Non-del in sample: {s['case_id']} -> {reason}")

evals = list(csv.DictReader(open('dataset/deletion_requests.csv', encoding='utf-8')))
non_dels = []
print('\nTesting 518 evaluation requests:')
for e in evals:
    is_del, reason = RequestClassifier.classify(e['request_text'])
    if not is_del:
        non_dels.append((e['case_id'], reason))

print(f'Total non-deletion requests detected: {len(non_dels)}')
for cid, reason in non_dels:
    print(f'  {cid}: {reason}')
