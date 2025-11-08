# py/services/shims/speech_shim.py
import time
from typing import Any, Dict
from py.services.shims.base_shim import BaseShim
import base64
import hashlib

class SpeechShim(BaseShim):
    def __init__(self, meta: Dict[str, Any]):
        super().__init__(meta)
        self._started = time.time()

    def predict(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        payload: { "audio_b64": "..." } OR { "audio_bytes": b"..." }
        Returns: { transcript: str, confidence: float }
        Replace with real ASR invocation (local model or cloud)
        """
        audio_b64 = payload.get("audio_b64")
        if not audio_b64 and payload.get("audio_bytes"):
            audio_b64 = base64.b64encode(payload["audio_bytes"]).decode("ascii")

        # Deterministic pseudo-transcript: hash the audio and return a fixed phrase
        fingerprint = hashlib.md5((audio_b64 or "").encode("utf-8")).hexdigest()[:8]
        transcript = f"[audio:{fingerprint}] simulated transcript"
        confidence = 0.88 if audio_b64 else 0.0

        return {
            "success": True,
            "payload": {
                "transcript": transcript,
                "confidence": confidence,
                "fingerprint": fingerprint
            },
            "meta": {"name": self.meta.get("name"), "version": self.meta.get("version")}
        }

    def health_check(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "name": self.meta.get("name"),
            "version": self.meta.get("version"),
            "uptime": time.time() - self._started,
            "details": "Speech shim ready (placeholder)"
        }