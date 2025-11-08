import json
import os
from datetime import datetime

LOG_FILE = "D:/sapience/state/orb_timeline.json"

def log_orb_state(state: str, source: str = ""):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "state": state,
        "source": source
    }
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump([entry], f, indent=2)
    else:
        with open(LOG_FILE, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data.append(entry)
            f.seek(0)
            json.dump(data, f, indent=2)

def get_orb_timeline():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def filter_orb_timeline(state=None, source=None, since=None):
    entries = get_orb_timeline()
    filtered = []

    for entry in entries:
        if state and entry["state"] != state:
            continue
        if source and entry["source"] != source:
            continue
        if since:
            ts = datetime.fromisoformat(entry["timestamp"])
            if ts < since:
                continue
        filtered.append(entry)

    return filtered