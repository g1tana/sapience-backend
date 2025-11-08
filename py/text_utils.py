"""
Text utilities for normalization and similarity without external dependencies.
"""

import re
from difflib import SequenceMatcher
from typing import List, Set, Tuple

import config


def normalize(text: str) -> str:
    t = text or ""
    if config.LOWERCASE:
        t = t.lower()
    if config.STRIP_PUNCTUATION:
        t = re.sub(r"[^\w\s]", " ", t)
    if config.COLLAPSE_WHITESPACE:
        t = re.sub(r"\s+", " ", t).strip()
    return t


def tokenize(text: str) -> List[str]:
    t = normalize(text)
    tokens = [tok for tok in t.split(" ") if tok]
    if config.REMOVE_STOPWORDS:
        tokens = [tok for tok in tokens if tok not in config.STOPWORDS]
    return tokens


def token_set(text: str) -> Set[str]:
    return set(tokenize(text))


def jaccard_like(a: Set[str], b: Set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / max(1, union)


def char_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()


def best_match_to_intents(
    phrase: str, intent_keywords: dict
) -> Tuple[str, float]:
    """
    Returns (best_intent, score) using combined token + char similarity.
    1) Compare phrase against each keyword across intents.
    2) Keep best score and intent.
    """
    phrase_tokens = token_set(phrase)
    best_intent = None
    best_score = 0.0

    for intent, keywords in intent_keywords.items():
        for kw in keywords:
            ts = jaccard_like(phrase_tokens, token_set(kw))
            cs = char_similarity(phrase, kw)
            score = max(ts, cs)
            if score > best_score:
                best_score = score
                best_intent = intent

    return best_intent, best_score