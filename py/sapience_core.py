"""
Conversational core:
- Identify speaker
- Build context (speaker history, facts, global facts)
- Generate answer via LLM
- Call local tools deterministically when needed
- Persist memory
"""

import os
import json
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

import config
from tools import tool_time, tool_status, tool_location
from memory_store import MemoryStore

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class SapienceCore:
    def __init__(self):
        self.mem = MemoryStore()

    # Tool router the LLM can request via simple markers
    def call_tool(self, name: str) -> Optional[str]:
        if name == "time": return tool_time()
        if name == "status": return tool_status()
        if name == "location": return tool_location()
        return None

    def _llm(self, prompt: Dict[str, Any]) -> str:
        if not config.USE_LLM_FALLBACK or not OPENAI_API_KEY:
            return "I’m ready to help, but generative answers are currently disabled."
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": config.LLM_MODEL,
            "max_tokens": config.LLM_MAX_TOKENS,
            "temperature": config.LLM_TEMPERATURE,
            "messages": prompt["messages"]
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()

    def build_context(self, speaker_name: Optional[str]) -> Dict[str, Any]:
        speaker_ctx = self.mem.get_speaker(speaker_name) if speaker_name else {"facts": [], "history": []}
        system = (
            f"{config.SYSTEM_PERSONA} "
            f"Available tools: time(), status(), location(). "
            "When you need these, respond with a single line: <tool:NAME>. "
            "Otherwise, answer directly."
        )
        facts = speaker_ctx.get("facts", [])
        hist = speaker_ctx.get("history", [])
        gfacts = self.mem.global_mem.get("facts", [])
        messages = [{"role": "system", "content": system}]
        if facts:
            messages.append({"role": "system", "content": "Known speaker facts: " + "; ".join(facts)})
        if gfacts:
            messages.append({"role": "system", "content": "Global facts: " + "; ".join(gfacts)})
        # Lightweight history priming
        for h in hist[-5:]:
            messages.append({"role": "user", "content": h.get("user", "")})
            messages.append({"role": "assistant", "content": h.get("assistant", "")})
        return {"messages": messages}

    def generate_reply(self, text: str, speaker_name: Optional[str]) -> str:
        # Build context
        ctx = self.build_context(speaker_name)
        ctx["messages"].append({"role": "user", "content": text})

        # Ask LLM
        try:
            raw = self._llm(ctx)
        except Exception as e:
            raw = f"Sorry, I hit an issue fetching an answer. {e}"

        # Tool trigger: let LLM request a local deterministic value
        if raw.strip().startswith("<tool:") and raw.strip().endswith(">"):
            tool_name = raw.strip()[6:-1].strip().lower()
            result = self.call_tool(tool_name)
            if result is not None:
                # Replace with a natural sentence
                if tool_name == "time":
                    reply = f"The current time is {result}."
                elif tool_name == "status":
                    reply = result
                elif tool_name == "location":
                    reply = result
                else:
                    reply = f"{tool_name}: {result}"
            else:
                reply = "I couldn’t access that tool."
        else:
            reply = raw

        # Persist exchange
        self.mem.append_global_history({"user": text, "assistant": reply})
        if speaker_name:
            self.mem.append_speaker_history(speaker_name, {"user": text, "assistant": reply})
        self.mem.log_transcript({"speaker": speaker_name or "Unknown", "user": text, "assistant": reply})

        return reply