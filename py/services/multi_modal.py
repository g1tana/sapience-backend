from ingest import ingest_file
from vision import ingest_image
from executor import execute
import os

def handle_input(source: str, payload: dict) -> str:
    if source == "text":
        query = payload["text"]
        return execute(query)

    if source == "voice":
        transcript = payload["text"]
        return execute(transcript)

    if source == "file":
        path = payload["path"]
        tags = payload.get("tags", [])
        ingest_file(path, tags)
        return f"Ingested file: {os.path.basename(path)}"

    if source == "image":
        data = payload["base64"]
        tags = payload.get("tags", [])
        caption = ingest_image(data, tags)
        return f"Image ingested: {caption}"

    return "Unsupported input type."