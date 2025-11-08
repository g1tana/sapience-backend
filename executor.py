from memory import search_memory, store_memory
from plugin_loader import route_to_plugin
from tasks import create_task
from orb import set_orb_state
from voice import respond
import ollama

def execute(text: str) -> str:
    set_orb_state("thinking")
    lowered = text.lower()

    # 🔹 Task creation
    if "create task:" in lowered:
        name = text.split("create task:")[1].strip()
        create_task(name, steps=[])
        store_memory(text, { "source": "task_created" })
        set_orb_state("idle")
        reply = f"Task created: {name}"
        respond(reply)
        return reply

    # 🔹 Plugin routing
    plugin_response = route_to_plugin(text)
    if plugin_response and "No matching plugin" not in plugin_response:
        store_memory(text, { "source": "plugin_trigger" })
        set_orb_state("executing")
        set_orb_state("idle")
        respond(plugin_response)
        return plugin_response

    # 🔹 LLM fallback with memory context
    context = search_memory(text)
    context_text = "\n".join([r[0] for r in context])

    try:
        response = ollama.chat(
            model="llama3",
            messages=[
                { "role": "system", "content": f"Use this context:\n{context_text}" },
                { "role": "user", "content": text }
            ]
        )
        reply = response["message"]["content"].strip()
    except Exception as e:
        reply = f"⚠️ Model failed: {e}"

    store_memory(reply, { "source": "model" })
    set_orb_state("idle")
    respond(reply)
    return reply