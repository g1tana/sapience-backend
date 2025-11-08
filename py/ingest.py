from utils.files import read_file
from memory import store_memory
import os

def ingest_file(path: str, tags: list = []):
    content = read_file(path)
    if not content:
        print(f"[Ingest] Unsupported or empty file: {path}")
        return

    metadata = {
        "source": "file",
        "path": path,
        "tags": tags
    }

    store_memory(content, metadata)
    print(f"[Ingest] Stored: {path}")