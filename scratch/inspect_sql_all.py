import glob
import sqlite3
import os

sql_files = glob.glob(r'C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26\dataset\evidence\databases\*.sql')
all_tables = set()
table_schemas = {}
for f in sql_files:
    conn = sqlite3.connect(':memory:')
    with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
        conn.executescript(fp.read())
    cur = conn.cursor()
    cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
    for name, sql in cur.fetchall():
        all_tables.add(name)
        if name not in table_schemas:
            table_schemas[name] = sql
    conn.close()

print('All SQL tables:', sorted(all_tables))
for t in sorted(table_schemas):
    print(f"Table {t}:\n  {table_schemas[t]}")
