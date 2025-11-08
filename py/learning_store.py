"""
LearningStore
-------------
Dependency-free learning layer with:
- Unknown logging & capping
- Success counters
- Learned keywords persistence
- Proposal mechanism for safe auto-adaptation (accept/deny)
- Similarity-based intent suggestion

Files (config-controlled):
- data_unknown.json
- data_learned.json
- data_success.json
- data_proposals.json
"""

import json
import os
from typing import Dict, List, Optional, Tuple

import config
from text_utils import best_match_to_intents


class LearningStore:
    def __init__(self):
        self.unknown: List[str] = self._load_list(config.DATA_UNKNOWN)
        self.learned: Dict[str, List[str]] = self._load_dict(config.DATA_LEARNED)
        self.success: Dict[str, int] = self._load_dict(config.DATA_SUCCESS)
        self.proposals: Dict[str, List[str]] = self._load_dict(config.DATA_PROPOSALS)

    # --------------- Persistence helpers ---------------
    def _load_list(self, path: str) -> List[str]:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return list(data) if isinstance(data, list) else []
            except Exception:
                return []
        return []

    def _load_dict(self, path: str) -> Dict[str, List[str]]:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return dict(data) if isinstance(data, dict) else {}
            except Exception:
                return {}
        return {}

    def _save_list(self, path: str, data: List[str]) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _save_dict(self, path: str, data: Dict[str, List[str]]) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # --------------- Public API ---------------
    def log_unknown(self, phrase: str) -> None:
        phrase = phrase.strip()
        if not phrase:
            return
        if phrase not in self.unknown:
            self.unknown.append(phrase)
            # Cap size to avoid bloat
            if len(self.unknown) > config.MAX_UNKNOWN_LOG_SIZE:
                self.unknown = self.unknown[-config.MAX_UNKNOWN_LOG_SIZE:]
            self._save_list(config.DATA_UNKNOWN, self.unknown)
            print(f"[Learning] Logged unknown intent: {phrase}")

    def record_success(self, keyword: str) -> None:
        key = f"{keyword}"
        self.success[key] = int(self.success.get(key, 0)) + 1
        with open(config.DATA_SUCCESS, "w", encoding="utf-8") as f:
            json.dump(self.success, f, ensure_ascii=False, indent=2)

    def get_intent_keywords(self, intent_name: str) -> List[str]:
        return self.learned.get(intent_name, [])

    def learn_keyword(self, intent_name: str, phrase: str) -> None:
        phrase = phrase.strip()
        if not phrase:
            return
        existing = self.learned.get(intent_name, [])
        if phrase in existing:
            return
        if len(existing) >= config.MAX_LEARNED_PER_INTENT:
            print(f"[Learning] Skipped learning (limit reached) for '{intent_name}'")
            return
        existing.append(phrase)
        self.learned[intent_name] = existing
        self._save_dict(config.DATA_LEARNED, self.learned)
        print(f"[Learning] Learned new keyword for '{intent_name}': {phrase}")

    def propose_learning(self, intent_name: str, phrase: str) -> None:
        phrase = phrase.strip()
        if not phrase:
            return
        proposals = self.proposals.get(intent_name, [])
        if phrase not in proposals:
            proposals.append(phrase)
            self.proposals[intent_name] = proposals
            self._save_dict(config.DATA_PROPOSALS, self.proposals)
            print(f"[Learning] Proposed new keyword for '{intent_name}': {phrase}")

    def accept_proposal(self, intent_name: str, phrase: str) -> bool:
        proposals = self.proposals.get(intent_name, [])
        if phrase in proposals:
            proposals.remove(phrase)
            self.proposals[intent_name] = proposals
            self._save_dict(config.DATA_PROPOSALS, self.proposals)
            self.learn_keyword(intent_name, phrase)
            return True
        return False

    def deny_proposal(self, intent_name: str, phrase: str) -> bool:
        proposals = self.proposals.get(intent_name, [])
        if phrase in proposals:
            proposals.remove(phrase)
            self.proposals[intent_name] = proposals
            self._save_dict(config.DATA_PROPOSALS, self.proposals)
            print(f"[Learning] Denied proposal for '{intent_name}': {phrase}")
            return True
        return False

    def find_best_intent_match(
        self, phrase: str, intent_keywords: Dict[str, List[str]]
    ) -> Optional[Tuple[str, float]]:
        best_intent, score = best_match_to_intents(phrase, intent_keywords)
        return (best_intent, score) if best_intent else None