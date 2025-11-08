def plugin(func):
    """
    Marks a function as a Sapience plugin.
    This allows plugin_loader.py to auto-register it.
    """
    func._is_plugin = True
    return func