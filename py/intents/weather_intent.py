# intents/weather_intent.py
KEYWORDS = ["weather", "forecast", "rain"]

def handle(user_text: str) -> str:
    return "I can’t forecast yet, but I’ve noted your interest in weather."