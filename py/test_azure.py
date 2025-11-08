import os
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

def main():
    # Load environment variables from .env
    load_dotenv()

    azure_key = os.getenv("AZURE_KEY")
    azure_region = os.getenv("AZURE_REGION")

    if not azure_key or not azure_region:
        print("❌ Missing AZURE_KEY or AZURE_REGION in .env")
        return

    # Configure Azure Speech
    speech_config = speechsdk.SpeechConfig(
        subscription=azure_key,
        region=azure_region
    )

    # Use a supported UK South neural voice
    speech_config.speech_synthesis_voice_name = "en-GB-SoniaNeural"

    # Output to default speaker
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

    # Create synthesizer
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    # Speak a test phrase
    print("🔊 Speaking test phrase with Azure Sonia (UK South)...")
    result = synthesizer.speak_text_async(
        "Hello Gavin, this is Sonia speaking from Azure UK South."
    ).get()

    # Check result
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("✅ Speech synthesis completed successfully.")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation = result.cancellation_details
        print("❌ Speech synthesis canceled.")
        print("Reason:", cancellation.reason)
        print("Error details:", cancellation.error_details)

if __name__ == "__main__":
    main()