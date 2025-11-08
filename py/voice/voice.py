import os
import yaml
import pyttsx3
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Load voice configuration
CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "voices.yaml"
with open(CONFIG_PATH, "r") as f:
    VOICE_CONFIG = yaml.safe_load(f)

# API keys
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
AZURE_KEY = os.getenv("AZURE_KEY")  # optional, if you add Azure later

# -------------------------
# Core Voice Manager
# -------------------------

class VoiceManager:
    def __init__(self):
        self.fallback_order = VOICE_CONFIG.get("fallback_order", ["system"])

    def speak(self, text: str, module: str = "sapience"):
        """Speak text using the configured engine for a given module."""
        module_cfg = VOICE_CONFIG["modules"].get(module, {})
        engine = module_cfg.get("engine")

        # Try preferred engine first
        if engine == "elevenlabs" and ELEVEN_API_KEY:
            try:
                return self._speak_elevenlabs(text, module_cfg)
            except Exception as e:
                print(f"[Voice] ElevenLabs failed: {e}")

        if engine == "azure" and AZURE_KEY:
            try:
                return self._speak_azure(text, module_cfg)
            except Exception as e:
                print(f"[Voice] Azure failed: {e}")

        if engine == "system":
            try:
                return self._speak_system(text, module_cfg)
            except Exception as e:
                print(f"[Voice] System TTS failed: {e}")

        # Fallback chain
        for fallback in self.fallback_order:
            if fallback == "elevenlabs" and ELEVEN_API_KEY:
                try:
                    return self._speak_elevenlabs(text, VOICE_CONFIG["elevenlabs"])
                except Exception:
                    continue
            if fallback == "azure" and AZURE_KEY:
                try:
                    return self._speak_azure(text, VOICE_CONFIG["azure"])
                except Exception:
                    continue
            if fallback == "system":
                return self._speak_system(text, VOICE_CONFIG["system"])

        raise RuntimeError("No available TTS engine succeeded.")

    # -------------------------
    # Engines
    # -------------------------

    def _speak_elevenlabs(self, text, cfg):
        voice_id = cfg.get("voice_id")
        model = VOICE_CONFIG["elevenlabs"]["model"]
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        headers = {
            "xi-api-key": ELEVEN_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": model,
            "voice_settings": {
                "stability": VOICE_CONFIG["elevenlabs"]["stability"],
                "similarity_boost": VOICE_CONFIG["elevenlabs"]["similarity_boost"]
            }
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        out_file = "response.wav"
        with open(out_file, "wb") as f:
            f.write(response.content)

        os.system(f'start {out_file}')  # Windows playback
        return out_file

    def _speak_azure(self, text, cfg):
        # Placeholder for Azure TTS integration
        # You’d use azure.cognitiveservices.speech SDK here
        print(f"[Voice] Azure TTS (stub): {text}")
        return None

    def _speak_system(self, text, cfg):
        engine = pyttsx3.init()
        voice_name = cfg.get("default_voice", "Hazel")
        for v in engine.getProperty("voices"):
            if voice_name.lower() in v.name.lower():
                engine.setProperty("voice", v.id)
                break
        engine.say(text)
        engine.runAndWait()
        return None


# -------------------------
# Example usage
# -------------------------
if __name__ == "__main__":
    vm = VoiceManager()
    vm.speak("Sapience voice layer is online.", module="sapience")
    vm.speak("Orb module speaking.", module="orb")
    vm.speak("System confirmation.", module="system")