# py/services/shims/vision_shim.py
import time
from typing import Any, Dict
from py.services.shims.base_shim import BaseShim
import base64
import hashlib

class VisionShim(BaseShim):
    def __init__(self, meta: Dict[str, Any]):
        super().__init__(meta)
        self._started = time.time()

    def predict(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        payload can be:
          { "image_bytes": b"..."} OR { "image_b64": "..." }
        Returns:
          { labels: [...], embedding: [...], success: True }
        This shim returns simple deterministic placeholders; replace with real model call.
        """
        img_b64 = payload.get("image_b64")
        if not img_b64 and payload.get("image_bytes"):
            img_b64 = base64.b64encode(payload["image_bytes"]).decode("ascii")

        # create a lightweight deterministic fingerprint as pseudo-embedding
        fingerprint = hashlib.sha1((img_b64 or "").encode("utf-8")).hexdigest()[:16]
        labels = ["mystic_ring", "runes", "orb"] if img_b64 else []
        embedding = [int(fingerprint[i:i+4], 16) % 1000 for i in range(0, 16, 4)]

        return {
            "success": True,
            "payload": {
                "labels": labels,
                "embedding": embedding,
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
            "details": "Vision shim ready (placeholder)"
        }