import os
import azure.cognitiveservices.speech as speechsdk

AZURE_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_REGION = os.getenv("AZURE_SPEECH_REGION", "uksouth")

def recognize_speech(language: str = "en-GB") -> str:
    """
    Single-utterance recognition from default microphone.
    Returns recognized text or empty string.
    """
    if not AZURE_KEY:
        print("[Sapience] Missing AZURE_SPEECH_KEY.")
        return ""

    speech_config = speechsdk.SpeechConfig(subscription=AZURE_KEY, region=AZURE_REGION)
    speech_config.speech_recognition_language = language
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    print("[Sapience] Listening... (say 'quit' to exit)")
    result = recognizer.recognize_once_async().get()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text.strip()
    if result.reason == speechsdk.ResultReason.NoMatch:
        print("[Sapience] No speech recognized.")
        return ""
    if result.reason == speechsdk.ResultReason.Canceled:
        details = result.cancellation_details
        print(f"[Sapience] Recognition canceled: {details.reason}. {details.error_details or ''}")
        return ""
    return ""