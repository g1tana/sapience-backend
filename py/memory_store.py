"""
JSON-backed memory store for speakers and global context.
"""

import os, json
from typing import Dict, Any, List
import config

class MemoryStore:
    def __init__(self):
        os.makedirs(config.STORE_DIR, exist_ok=True)
        self.speakers: Dict[str, Dict[str, Any]] = self._load(config.SPEAKERS_FILE, default={})
        self.global_mem: Dict[str, Any] = self._load(config.GLOBAL_FILE, default={"facts": [], "history": []})

    def _load(self, path: str, default):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return default
        return default

    def _save(self, path: str, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # Speaker memory
    def get_speaker(self, name: str) -> Dict[str, Any]:
        return self.speakers.get(name, {"embedding": None, "facts": [], "history": []})

    def set_speaker(self, name: str, data: Dict[str, Any]):
        self.speakers[name] = data
        self._save(config.SPEAKERS_FILE, self.speakers)

    def append_speaker_fact(self, name: str, fact: str):
        s = self.get_speaker(name)
        s.setdefault("facts", []).append(fact)
        self.set_speaker(name, s)

    def append_speaker_history(self, name: str, exchange: Dict[str, str]):
        s = self.get_speaker(name)
        hist: List[Dict[str, str]] = s.setdefault("history", [])
        hist.append(exchange)
        # keep last N
        s["history"] = hist[-config.MAX_HISTORY_PER_SPEAKER:]
        self.set_speaker(name, s)

    # Global memory
    def append_global_fact(self, fact: str):
        self.global_mem.setdefault("facts", []).append(fact)
        self._save(config.GLOBAL_FILE, self.global_mem)

    def append_global_history(self, exchange: Dict[str, str]):
        self.global_mem.setdefault("history", []).append(exchange)
        self._save(config.GLOBAL_FILE, self.global_mem)

    # Transcripts
    def log_transcript(self, record: Dict[str, str]):
        with open(config.TRANSCRIPTS, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")