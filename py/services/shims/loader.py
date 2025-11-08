# py/services/shims/loader.py
import importlib
import json
import os
from typing import Dict, Any

REG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "models.json")

def load_registry(path: str = REG_PATH) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def instantiate_shim(entry: Dict[str, Any]):
    """
    entry: { name, version, impl, ... }
    impl: "py.services.shims.agent_shim.AgentShim"
    """
    impl = entry.get("impl")
    if not impl:
        raise ValueError("No impl specified for registry entry")
    module_path, class_name = impl.rsplit(".", 1)
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    # Pass entry metadata to the shim
    return cls(entry)

def instantiate_all():
    reg = load_registry()
    out = {}
    for key, entry in reg.get("models", {}).items():
        out[key] = instantiate_shim(entry)
    return out

if __name__ == "__main__":
    shims = instantiate_all()
    for k, s in shims.items():
        print(k, s.meta)