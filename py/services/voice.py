import os
import requests
import numpy as np
import sounddevice as sd

ELEVEN_KEY = os.getenv("ELEVEN_API_KEY")
ELEVEN_VOICE_ID = os.getenv("ELEVEN_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

def speak_with_elevenlabs(text: str, samplerate: int = 22050):
    """
    Synchronously synthesize with ElevenLabs and play through default speaker.
    """
    if not ELEVEN_KEY:
        print("[Sapience] Missing ELEVEN_API_KEY.")
        return

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}"
    headers = {"xi-api-key": ELEVEN_KEY, "Content-Type": "application/json"}
    payload = {"text": text, "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}}

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        audio = np.frombuffer(resp.content, dtype=np.int16)
        sd.play(audio, samplerate=samplerate)
        sd.wait()
    except Exception as e:
        print(f"[Sapience] ElevenLabs error: {e}")