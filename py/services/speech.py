import speech_recognition as sr
import pyttsx3
from memory import store_memory
from orb import route_command
from voice import respond

recognizer = sr.Recognizer()
tts = pyttsx3.init()
silent_mode = False

def voice_only_loop(force_local: bool = False):
    global silent_mode
    while True:
        try:
            with sr.Microphone() as mic:
                print("🎙️ Listening...")
                audio = recognizer.listen(mic)

            text = recognizer.recognize_google(audio)
            print("🧠 Heard:", text)

            lowered = text.lower()

            # 🔹 Silent mode toggle
            if "silent mode" in lowered or "stop speaking" in lowered:
                silent_mode = True
                respond("Okay, I’ll stay quiet.")
                continue

            if "speak again" in lowered or "voice on" in lowered:
                silent_mode = False
                respond("Voice mode reactivated.")
                continue

            # 🔹 Store voice input
            store_memory(text, {
                "source": "voice",
                "modality": "audio"
            }, force_local=force_local)

            # 🔹 Spoken confirmation
            if not silent_mode:
                respond(text)

            # 🔹 Route to Orb
            route_command(text, force_local=force_local)

        except sr.UnknownValueError:
            if not silent_mode:
                respond("Sorry, I didn't catch that.")
        except sr.RequestError as e:
            if not silent_mode:
                respond("Speech recognition failed.")

# 🔹 Start the loop
voice_only_loop()