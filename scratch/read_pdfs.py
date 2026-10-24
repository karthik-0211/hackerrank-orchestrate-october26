import os
import sys
from pypdf import PdfReader

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")
pdf_dir = os.path.join(DATASET_DIR, "evidence", "documents")

for f in sorted(os.listdir(pdf_dir)):
    fpath = os.path.join(pdf_dir, f)
    reader = PdfReader(fpath)
    print(f"\n==================== PDF: {f} (Pages: {len(reader.pages)}) ====================")
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        print(f"--- Page {i+1} ---")
        print(text)
