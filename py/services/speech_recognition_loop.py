import speech_recognition as sr

def transcribe_from_mic():
    """Continuously listen to the microphone and yield recognized text."""
    recognizer = sr.Recognizer()

    # Use the default system microphone
    with sr.Microphone() as source:
        print("🎤 Calibrating microphone for ambient noise (2s)...")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print(f"🔧 Energy threshold set to {recognizer.energy_threshold}")
        print("✅ Ready. Speak clearly — say 'quit' to exit.\n")

        while True:
            try:
                print("Listening...")
                # Listen with timeout and phrase limit
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

                # Recognize speech using Google Web Speech API
                text = recognizer.recognize_google(audio)
                print(f"[You] {text}")

                if text.strip().lower() in {"quit", "exit", "stop"}:
                    print("👋 Exiting speech loop.")
                    break

                yield text

            except sr.WaitTimeoutError:
                print("[Info] No speech detected (timeout).")
            except sr.UnknownValueError:
                print("[Info] Could not understand audio.")
            except sr.RequestError as e:
                print(f"[Error] Recognition service unavailable: {e}")

def main():
    for sentence in transcribe_from_mic():
        # Here’s where you’d hand off to Sapience backend
        # For now, just echo back
        print(f"[Sapience] I heard: {sentence}")

if __name__ == "__main__":
    main()