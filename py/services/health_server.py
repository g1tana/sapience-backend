# py/services/health_server.py
from flask import Flask, jsonify
from py.orchestrator_shim_integration import ShimOrchestrator
import logging

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
orch = ShimOrchestrator()

@app.route("/health", methods=["GET"])
def health():
    return jsonify(orch.health())

@app.route("/run_alignment", methods=["POST"])
def run_alignment():
    # Minimal: accept JSON with image_b64 / audio_b64
    from flask import request
    payload = request.get_json() or {}
    res = orch.run_alignment_task(image_b64=payload.get("image_b64"), audio_b64=payload.get("audio_b64"),
                                  instruction=payload.get("instruction", "Align orb to centre"))
    return jsonify(res)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)