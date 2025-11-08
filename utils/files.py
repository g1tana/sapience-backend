import os

def read_file(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".txt":
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    if ext == ".md":
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    if ext == ".py":
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    # Add support for PDF, DOCX, etc. later
    return ""