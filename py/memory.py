import json
import os
from db import get_db, save_db
import openai
from sentence_transformers import SentenceTransformer
from config import USE_LOCAL_EMBEDDINGS

MEMORY_FILE = "D:/sapience/state/memory.json"
LOCAL_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

def embed_openai(text: str) -> list:
    try:
        response = openai.Embedding.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response["data"][0]["embedding"]
    except Exception:
        return None

def embed_local(text: str) -> list:
    return LOCAL_MODEL.encode(text).tolist()

def embed_text(text: str, force_local: bool = False) -> dict:
    if force_local or USE_LOCAL_EMBEDDINGS:
        return { "local": embed_local(text) }

    remote = embed_openai(text)
    local = embed_local(text)

    return {
        "openai": remote,
        "local": local
    }

def store_memory(text: str, meta: dict, force_local: bool = False):
    embeddings = embed_text(text, force_local)
    entry = {
        "text": text,
        "meta": {
            **meta,
            "embedding_openai": embeddings.get("openai"),
            "embedding_local": embeddings.get("local")
        }
    }
    data = get_db()
    data.append(entry)
    save_db(data)

def search_memory(query: str):
    data = get_db()
    results = []
    for entry in data:
        if query.lower() in entry["text"].lower():
            results.append((entry["text"], entry["meta"]))
    return results

def semantic_search(query: str, top_k: int = 5, use_local: bool = False):
    query_vec = embed_local(query) if use_local or USE_LOCAL_EMBEDDINGS else embed_openai(query)
    key = "embedding_local" if use_local or USE_LOCAL_EMBEDDINGS else "embedding_openai"

    data = get_db()
    scored = []

    for entry in data:
        entry_vec = entry["meta"].get(key)
        if entry_vec:
            score = cosine_similarity(query_vec, entry_vec)
            scored.append((score, entry["text"], entry["meta"]))

    scored.sort(reverse=True)
    return [(text, meta) for score, text, meta in scored[:top_k]]

def cosine_similarity(a, b):
    dot = sum(x*y for x, y in zip(a, b))
    norm_a = sum(x*x for x in a) ** 0.5
    norm_b = sum(x*x for x in b) ** 0.5
    return dot / (norm_a * norm_b + 1e-8)