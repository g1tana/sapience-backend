import os
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

# Load .env
load_dotenv()

print("AZURE_KEY present:", bool(os.getenv("AZURE_KEY")))
print("AZURE_REGION:", os.getenv("AZURE_REGION"))

speech_config = speechsdk.SpeechConfig(
    subscription=os.getenv("AZURE_KEY"),
    region=os.getenv("AZURE_REGION")
)
speech_config.speech_synthesis_voice_name = "en-GB-SoniaNeural"
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

synthesizer = speechsdk.SpeechSynthesizer(
    speech_config=speech_config,
    audio_config=audio_config
)

print("🔊 Attempting Azure synthesis...")
result = synthesizer.speak_text_async("This is a direct Azure test of Sonia.").get()

print("Result:", result.reason)
if result.reason == speechsdk.ResultReason.Canceled:
    cancellation = result.cancellation_details
    print("Cancellation reason:", cancellation.reason)
    print("Error details:", cancellation.error_details)