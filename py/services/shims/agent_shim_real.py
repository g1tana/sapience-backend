# py/services/shims/agent_shim_real.py
import time
from typing import Any, Dict
from py.services.shims.base_shim import BaseShim

# Try to import your existing chat wrapper; adapt the import if your module path differs
try:
    from sapience_chat import ask as chat_ask  # example: functions exposed by sapience_chat.py
except Exception:
    chat_ask = None

class AgentShimReal(BaseShim):
    def __init__(self, meta: Dict[str, Any]):
        super().__init__(meta)
        self._started = time.time()

    def predict(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        inp = payload.get("input", "")
        context = payload.get("context", {})
        # If a real chat API exists, call it
        if chat_ask:
            try:
                # Example: chat_ask(prompt, context) -> returns text or dict
                response = chat_ask(inp, context=context)
                return {"success": True, "payload": {"text": response}, "meta": self.meta}
            except Exception as e:
                return {"success": False, "error": str(e), "meta": self.meta}
        # Fallback deterministic behavior
        plan = f"agent(real-fallback): {inp[:120]}"
        return {"success": True, "payload": {"text": plan, "plan": {"steps": []}}, "meta": self.meta}

    def health_check(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "name": self.meta.get("name"),
            "version": self.meta.get("version"),
            "uptime": time.time() - self._started,
            "details": "Agent shim real (calls sapience_chat if available)"
        }   