import json

d = json.load(open('dataset/evidence/records/service_resource_export_20260915_114455.json', encoding='utf-8'))
for k, v in d['service_exports'].items():
    subk = list(v.keys())[0]
    for it in v[subk]:
        rid = it.get('resource_id')
        cust_ref = it.get("customer_reference") or it.get("subject_reference")
        email_or_query = it.get("email") or it.get("owner_email") or it.get("query") or it.get("requester_email") or it.get("customer_email")
        if isinstance(it.get("profile"), dict):
            email_or_query = it["profile"].get("email")
        print(f"{k:<20} | {subk:<16} | {rid:<18} | ref={cust_ref} | email={email_or_query}")
