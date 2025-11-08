"""
Deterministic local tools Sapience can call for reliable data.
"""

from datetime import datetime

def tool_time() -> str:
    return datetime.now().strftime("%H:%M")

def tool_status() -> str:
    return "Running smoothly and ready to help."

def tool_location() -> str:
    return "Operating locally inside the Sapience system."