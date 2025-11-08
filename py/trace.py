import json
import os
from datetime import datetime

TRACE_FILE = "D:/sapience/state/plugin_trace.json"

def log_plugin_trace(plugin: str, input_text: str, output_text: str, duration: float):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "plugin": plugin,
        "input": input_text,
        "output": output_text,
        "duration": duration
    }
    if not os.path.exists(TRACE_FILE):
        with open(TRACE_FILE, "w", encoding="utf-8") as f:
            json.dump([entry], f, indent=2)
    else:
        with open(TRACE_FILE, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data.append(entry)
            f.seek(0)
            json.dump(data, f, indent=2)

def get_plugin_trace():
    if not os.path.exists(TRACE_FILE):
        return []
    with open(TRACE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)