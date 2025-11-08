import speech_recognition as sr
import pyttsx3
import requests
from time import sleep
import asyncio
from orb_server import orb_broadcast

# Initialize and tune voice engine
engine = pyttsx3.init()
engine.setProperty("rate", 180)       # Speed: 180 wpm
engine.setProperty("volume", 1.0)     # Volume: max

# Select preferred voice
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[1].id)  # Zira (or change index as needed)

def set_orb(state: str):
    try:
        asyncio.run(orb_broadcast(state))
    except Exception as e:
        print(f"[Orb] Failed to set state: {state} ({e})")

def speak_stream(response):
    buffer = ""
    for chunk in response.iter_content(chunk_size=128):
        text = chunk.decode("utf-8")
        buffer += text

        while "." in buffer or "\n" in buffer:
            if "." in buffer:
                sentence, buffer = buffer.split(".", 1)
            else:
                sentence, buffer = buffer.split("\n", 1)

            sentence = sentence.strip()
            if sentence:
                print(f"🗣️ Speaking: {sentence}")
                engine.say(sentence)
                engine.runAndWait()

    if buffer.strip():
        print(f"🗣️ Speaking: {buffer.strip()}")
        engine.say(buffer.strip())
        engine.runAndWait()

def listen_and_respond():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    set_orb("listening")
    print("🎙️ Say something to Sapience...")

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        query = recognizer.recognize_google(audio)
        set_orb("thinking")
        print(f"🧍 You said: {query}")

        response = requests.post(
            "http://127.0.0.1:8000/api/query",
            json={"text": query},
            stream=True
        )

        set_orb("speaking")
        print("🤖 Sapience is responding...")
        speak_stream(response)

    except sr.UnknownValueError:
        set_orb("error")
        print("❌ Could not understand audio.")
        engine.say("Sorry, I didn't catch that.")
        engine.runAndWait()
    except requests.RequestException as e:
        set_orb("error")
        print(f"❌ Backend error: {e}")
        engine.say("Something went wrong talking to the backend.")
        engine.runAndWait()

if __name__ == "__main__":
    while True:
        listen_and_respond()
        sleep(1)