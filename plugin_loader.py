import os
import importlib
import inspect

PLUGIN_DIR = "D:/Sapience/backend/plugins"

plugin_registry = {}

def load_plugins():
    for filename in os.listdir(PLUGIN_DIR):
        if filename.endswith(".py") and not filename.startswith("_"):
            module_name = filename[:-3]
            module_path = f"plugins.{module_name}"
            try:
                module = importlib.import_module(module_path)
                for name, func in inspect.getmembers(module, inspect.isfunction):
                    if hasattr(func, "_is_plugin"):
                        plugin_registry[name] = func
                        print(f"🔌 Registered plugin: {name}")
            except Exception as e:
                print(f"⚠️ Failed to load {module_name}: {e}")

def route_to_plugin(text: str) -> str:
    lowered = text.lower()
    for name, func in plugin_registry.items():
        if name in lowered:
            try:
                result = func(text)
                return f"✅ Plugin '{name}' executed: {result}"
            except Exception as e:
                return f"⚠️ Plugin '{name}' failed: {e}"
    return "🌀 No matching plugin found."