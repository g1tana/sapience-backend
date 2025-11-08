"""
Speaker identification using voice embeddings.
If resemblyzer is unavailable, gracefully degrades to 'Unknown'.
"""

import numpy as np
from typing import Optional, Tuple, Dict, Any, List
import config

try:
    from resemblyzer import VoiceEncoder, preprocess_wav
    RES_EMBED = True
    _encoder = VoiceEncoder()
except Exception:
    RES_EMBED = False
    _encoder = None

def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0: return 0.0
    return float(np.dot(a, b) / denom)

def embed_audio(raw_audio: np.ndarray, sample_rate: int) -> Optional[np.ndarray]:
    if not RES_EMBED or _encoder is None:
        return None
    # Expect mono float32 waveform
    try:
        wav = preprocess_wav(raw_audio, sample_rate)
        emb = _encoder.embed_utterance(wav)
        return emb.astype(np.float32)
    except Exception:
        return None

def match_speaker(embedding: np.ndarray, speakers: Dict[str, Dict[str, Any]]) -> Optional[Tuple[str, float]]:
    best_name, best_score = None, 0.0
    for name, data in speakers.items():
        emb = np.array(data.get("embedding"), dtype=np.float32) if data.get("embedding") is not None else None
        if emb is None: continue
        score = _cosine(embedding, emb)
        if score > best_score:
            best_name, best_score = name, score
    if best_name and best_score >= config.SPEAKER_SIMILARITY_THRESHOLD:
        return best_name, best_score
    return None