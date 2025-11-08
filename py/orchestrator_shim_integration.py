# py/orchestrator_shim_integration.py
from py.services.shims.loader import instantiate_all
import time
import logging

log = logging.getLogger("orchestrator_shim")
logging.basicConfig(level=logging.INFO)

class ShimOrchestrator:
    def __init__(self):
        self.shims = instantiate_all()
        self.started = time.time()

    def health(self):
        out = {}
        for name, shim in self.shims.items():
            try:
                out[name] = shim.health_check()
            except Exception as e:
                out[name] = {"ok": False, "error": str(e)}
        return {
            "ok": all(v.get("ok", False) for v in out.values()),
            "services": out,
            "uptime": time.time() - self.started
        }

    def run_alignment_task(self, image_b64=None, audio_b64=None, instruction="Align orb to centre"):
        """
        Example flow:
          - call vision.predict(image)
          - call speech.predict(audio)
          - call agent.predict({ input, context })
        Returns agent result dict
        """
        vision = self.shims.get("vision")
        speech = self.shims.get("speech")
        agent = self.shims.get("agent")

        ctx = {}
        if vision and image_b64:
            try:
                v = vision.predict({"image_b64": image_b64})
                ctx["vision"] = v.get("payload")
            except Exception as e:
                log.exception("vision predict failed")
                ctx["vision_error"] = str(e)

        if speech and audio_b64:
            try:
                s = speech.predict({"audio_b64": audio_b64})
                ctx["speech"] = s.get("payload")
            except Exception as e:
                log.exception("speech predict failed")
                ctx["speech_error"] = str(e)

        agent_payload = {"input": instruction, "context": ctx}
        if not agent:
            return {"success": False, "error": "agent shim not available"}
        try:
            result = agent.predict(agent_payload)
            return result
        except Exception as e:
            log.exception("agent predict failed")
            return {"success": False, "error": str(e)}