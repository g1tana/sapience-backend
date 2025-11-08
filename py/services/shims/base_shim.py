# py/services/shims/base_shim.py
import time
from typing import Any, Dict

class BaseShim:
    """
    Minimal shim contract for all models.
    - predict(input: dict) -> dict
    - health_check() -> dict
    - meta: dict (name/version/type/etc)
    """

    def __init__(self, meta: Dict[str, Any]):
        self.meta = meta

    def predict(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implement model inference here.
        Always return a dictionary with at least:
          { "success": bool, "payload": {...}, "meta": {...} }
        """
        raise NotImplementedError()

    def health_check(self) -> Dict[str, Any]:
        """Return { ok: bool, name, version, uptime, details }"""
        return {
            "ok": True,
            "name": self.meta.get("name"),
            "version": self.meta.get("version"),
            "uptime": 0,
            "details": "shim ok"
        }