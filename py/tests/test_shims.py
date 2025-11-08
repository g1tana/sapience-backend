# py/tests/test_shims.py
import pytest
from py.services.shims.loader import instantiate_all

def test_instantiate_shims():
    shims = instantiate_all()
    assert "vision" in shims and "speech" in shims and "agent" in shims

def test_vision_predict():
    shims = instantiate_all()
    v = shims["vision"].predict({"image_b64": "dummy-data"})
    assert v["success"] is True
    assert "labels" in v["payload"]

def test_speech_predict():
    shims = instantiate_all()
    s = shims["speech"].predict({"audio_b64": "dummy-audio"})
    assert s["success"] is True
    assert "transcript" in s["payload"]

def test_agent_predict():
    shims = instantiate_all()
    a = shims["agent"].predict({"input": "test", "context": {}})
    assert isinstance(a, dict)
    assert "success" in a