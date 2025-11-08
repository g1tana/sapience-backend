from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from multi_modal import handle_input
from tasks import get_tasks
from registry import register_plugin, search_plugins
import os

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    source: str
    payload: dict

@app.post("/api/input")
async def input_router(data: Query):
    reply = handle_input(data.source, data.payload)
    return { "reply": reply }

@app.get("/api/tasks")
def get_task_list():
    raw = get_tasks()
    tasks = []
    for id, name, steps, status in raw:
        tasks.append({
            "id": id,
            "name": name,
            "steps": steps,
            "status": status
        })
    return { "tasks": tasks }

@app.get("/api/plugins")
def list_plugins(tag: str = None):
    return { "plugins": search_plugins(tag) }

@app.post("/api/plugins")
def deploy_plugin(data: dict):
    name = data["name"]
    code = data["code"]
    tags = data.get("tags", [])

    plugin_dir = "D:/sapience/plugins"
    os.makedirs(plugin_dir, exist_ok=True)

    with open(f"{plugin_dir}/{name}.py", "w", encoding="utf-8") as f:
        f.write(code)

    register_plugin(name, tags)
    return { "message": f"Plugin '{name}' deployed successfully." }

@app.get("/")
def root():
    return { "status": "Sapience API is running." }