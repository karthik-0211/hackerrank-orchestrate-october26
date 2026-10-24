import re

fpath = r'dataset\evidence\logs\resource_lookup_trace_20260926_103856.log'
with open(fpath, 'r', encoding='utf-8') as f:
    for line in f:
        if 'javier' in line:
            matches = re.findall(r'(\w+)=(?:"([^"]*)"|(\S+))', line)
            clean_kv = {m[0]: (m[1] if m[1] else m[2]) for m in matches}
            print("Line:", line.strip())
            print("Clean KV:", clean_kv)
