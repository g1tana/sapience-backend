import os
import sys
import io
import openai
import requests
import numpy as np
import sounddevice as sd
import soundfile as sf
import azure.cognitiveservices.speech as speechsdk

from utils import (
    load_and_check_env,
    check_audio_devices,
    log_user,
    log_ai,
    log_info,
    log_error,
    retry_with_backoff,
)

# --- Azure Speech Recognition ---
def recognize_speech():
    speech_config = speechsdk.SpeechConfig(
        subscription=os.getenv("AZURE_SPEECH_KEY"),
        region=os.getenv("AZURE_SPEECH_REGION")
    )
    speech_config.speech_recognition_language = "en-GB"
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    log_info("Listening...")
    result = recognizer.recognize_once_async().get()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text.strip()
    elif result.reason == speechsdk.ResultReason.NoMatch:
        return ""
    elif result.reason == speechsdk.ResultReason.Canceled:
        details = result.cancellation_details
        log_error(f"Azure canceled: {details.reason}, {details.error_details}")
        return ""
    return ""

# --- OpenAI Response ---
@retry_with_backoff
def generate_response(prompt):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    resp = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return resp["choices"][0]["message"]["content"].strip()

# --- ElevenLabs Speech ---
@retry_with_backoff
def speak_text(text):
    url = "https://api.elevenlabs.io/v1/text-to-speech/EXAVITQu4vr4xnSDxMaL"  # Example voice ID
    headers = {
        "xi-api-key": os.getenv("ELEVEN_API_KEY"),
        "Accept": "audio/wav",   # request WAV output
        "Content-Type": "application/json"
    }
    payload = {"text": text, "voice_settings": {"stability": 0.4, "similarity_boost": 0.8}}

    r = requests.post(url, headers=headers, json=payload)
    r.raise_for_status()

    # Decode WAV properly
    data, samplerate = sf.read(io.BytesIO(r.content), dtype="int16")
    sd.play(data, samplerate)
    sd.wait()

# --- Main Loop ---
def main():
    load_and_check_env()
    check_audio_devices()
    log_info("Sapience ready. Say 'quit' to exit.\n")

    while True:
        user_text = recognize_speech()
        if not user_text:
            continue
        log_user(user_text)

        # Exit check BEFORE OpenAI
        if user_text.lower() in ["quit", "exit", "stop"]:
            log_info("Goodbye.")
            break

        reply = generate_response(user_text)
        log_ai(reply)
        speak_text(reply)

if __name__ == "__main__":
    main()