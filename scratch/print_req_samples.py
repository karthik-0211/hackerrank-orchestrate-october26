import csv

evals = list(csv.DictReader(open('dataset/deletion_requests.csv', encoding='utf-8')))
for e in evals:
    if e['case_id'] in ['case_191', 'case_192', 'case_202', 'case_203']:
        print(f"{e['case_id']}: {e['request_text']}")
