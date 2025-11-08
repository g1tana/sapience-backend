from memory import search_memory

def get_memory_entries(query: str = "", source: str = ""):
    results = search_memory(query)
    filtered = []

    for text, meta in results:
        if source and meta.get("source") != source:
            continue
        filtered.append({ "text": text, "source": meta.get("source", "unknown") })

    return filtered