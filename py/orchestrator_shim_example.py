# py/orchestrator_shim_example.py
import os
import time
import json
import requests

# Simple local health URL used by the project
HEALTH_URL = os.environ.get("PY_HEALTH_URL", "http://127.0.0.1:5000/health")

def print_health():
    try:
        r = requests.get(HEALTH_URL, timeout=5)
        r.raise_for_status()
        data = r.json()
        print("ok      :", data.get("ok"))
        print("services:", data.get("services"))
        print("uptime  :", data.get("uptime"))
    except Exception as e:
        print("Failed to fetch health from", HEALTH_URL)
        print("Error:", type(e).__name__, str(e))

def demo_shim_calls():
    # Minimal demo stubs that mimic shim behavior.
    # Replace these with actual shim imports / calls when available.
    print("\n--- Demo shim predictions ---")
    # Vision demo
    vision_out = {"label": "cat", "confidence": 0.92}
    print("Vision:", json.dumps(vision_out))
    # Speech demo
    speech_out = {"transcript": "hello world", "confidence": 0.87}
    print("Speech:", json.dumps(speech_out))
    # Agent demo
    agent_out = {"response": "Acknowledged. Running task.", "task_id": "demo-1234"}
    print("Agent:", json.dumps(agent_out))

if __name__ == "__main__":
    print("Orchestrator shim example — fetching health from:", HEALTH_URL)
    print_health()
    demo_shim_calls()
    print("\nFinished. If the health call failed, start the Python health server first:")
    print("  .\\.venv\\Scripts\\python.exe py/services/health_server.py")