import os
import sys

REPO_ROOT = r"C:\Users\karthik\.gemini\antigravity-ide\scratch\hackerrank-orchestrate-october26"
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")

# Check what PDF packages might be available
for pkg in ["pypdf", "pdfplumber", "fitz", "pypdf2", "pdfminer"]:
    try:
        __import__(pkg)
        print(f"Available: {pkg}")
    except ImportError:
        pass

# Let's inspect the raw bytes of the 4 PDFs
pdf_dir = os.path.join(DATASET_DIR, "evidence", "documents")
for f in os.listdir(pdf_dir):
    fpath = os.path.join(pdf_dir, f)
    size = os.path.getsize(fpath)
    print(f"PDF: {f} ({size} bytes)")
    with open(fpath, "rb") as fp:
        raw = fp.read()
        # Look for text streams or string objects
        text_parts = []
        for line in raw.split(b"\n"):
            if b"(" in line and b")" in line and (b"Tj" in line or b"TJ" in line):
                text_parts.append(line.decode("latin1", errors="ignore"))
        print(f"  Sample text chunks: {len(text_parts)}")
        for tp in text_parts[:5]:
            print(f"    {tp.strip()}")
