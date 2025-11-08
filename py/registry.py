PLUGIN_META = {}

def register_plugin(name: str, tags: list, permissions: dict = None):
    PLUGIN_META[name] = {
        "tags": tags,
        "permissions": permissions or {}
    }

def search_plugins(tag: str = None):
    if not tag:
        return list(PLUGIN_META.keys())
    return [name for name, meta in PLUGIN_META.items() if tag in meta["tags"]]

def get_plugin_meta(name: str):
    return PLUGIN_META.get(name, {})