from datetime import datetime

KEYWORDS = ["time", "clock", "current time", "what time"]

def handle(user_text: str) -> str:
    return f"The current time is {datetime.now().strftime('%H:%M')}."