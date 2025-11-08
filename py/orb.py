import json
import os
from memory import store_memory
from voice import respond  # ✅ Updated to avoid circular import

STATE_FILE = "D:/sapience/state/orb.json"

def get_orb_state():
    if not os.path.exists(STATE_FILE):
        return { "state": "idle" }
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def set_orb_state(state: str):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({ "state": state }, f)

def load_orb():
    set_orb_state("ready")
    print("🌀 Orb loaded and ready.")
    respond("Orb is loaded and ready.")

def route_command(text: str, force_local: bool = False):
    lowered = text.lower()
    matched = False

    if "open browser" in lowered:
        os.system("start chrome")
        set_orb_state("executed: open browser")
        respond("Opening your browser now.")
        matched = True

    elif "shutdown" in lowered:
        if "confirm shutdown" in lowered:
            os.system("shutdown /s /t 1")
            set_orb_state("executed: shutdown")
            respond("Shutting down the system now.")
            matched = True
        else:
            set_orb_state("awaiting confirmation")
            respond("Are you sure you want to shut down? Say 'confirm shutdown' to proceed.")
            matched = True

    if matched:
        store_memory(text, {
            "source": "orb",
            "modality": "text",
            "tag": "matched"
        }, force_local=force_local)
    else:
        set_orb_state("idle")
        print("🌀 No matching command.")
        respond("I didn’t recognize that command, but I’ve saved it for later.")
        store_memory(text, {
            "source": "orb",
            "modality": "text",
            "tag": "unmatched"
        }, force_local=force_local)