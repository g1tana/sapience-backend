"""
CLI to review auto-learning proposals and unknown phrases.
- List proposals per intent
- Accept or deny proposals
- Inspect unknown log
"""

import json
import sys
import config
from learning_store import LearningStore

def load_json(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def save_json(path: str, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def list_proposals():
    store = LearningStore()
    print("Proposals:")
    for intent, phrases in store.proposals.items():
        for p in phrases:
            print(f" - [{intent}] {p}")

def accept(intent: str, phrase: str):
    store = LearningStore()
    if store.accept_proposal(intent, phrase):
        print(f"Accepted: [{intent}] {phrase}")
    else:
        print("Nothing accepted. Check intent/phrase.")

def deny(intent: str, phrase: str):
    store = LearningStore()
    if store.deny_proposal(intent, phrase):
        print(f"Denied: [{intent}] {phrase}")
    else:
        print("Nothing denied. Check intent/phrase.")

def show_unknown(limit: int = 50):
    unknown = load_json(config.DATA_UNKNOWN) or []
    print(f"Unknown phrases (latest {limit}):")
    for p in unknown[-limit:]:
        print(f" - {p}")

def main():
    args = sys.argv[1:]
    if not args:
        print("Usage:")
        print("  python review_learning.py proposals")
        print("  python review_learning.py accept <intent> <phrase>")
        print("  python review_learning.py deny <intent> <phrase>")
        print("  python review_learning.py unknown [limit]")
        return

    cmd = args[0]
    if cmd == "proposals":
        list_proposals()
    elif cmd == "accept" and len(args) >= 3:
        accept(args[1], " ".join(args[2:]))
    elif cmd == "deny" and len(args) >= 3:
        deny(args[1], " ".join(args[2:]))
    elif cmd == "unknown":
        limit = int(args[1]) if len(args) >= 2 else 50
        show_unknown(limit)
    else:
        print("Invalid command. Run without args for usage.")

if __name__ == "__main__":
    main()