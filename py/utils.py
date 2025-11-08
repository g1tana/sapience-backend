import os
import sys
import time
import random
import re
import sounddevice as sd
from dotenv import load_dotenv
from rich.console import Console
from rich.traceback import install

# Setup rich logging globally
install()
console = Console()

def load_and_check_env():
    """Load .env and verify all required keys are present."""
    load_dotenv()
    required = ["AZURE_SPEECH_KEY", "AZURE_SPEECH_REGION", "OPENAI_API_KEY", "ELEVEN_API_KEY"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        console.print(f"[bold red]Missing environment variables:[/bold red] {', '.join(missing)}")
        sys.exit(1)
    console.print("[green]✓ All environment variables loaded[/green]")

def pick_device_index(name_contains: str, kind: str) -> int | None:
    """Find a device index whose name contains the given substring (case-insensitive)."""
    devices = sd.query_devices()
    name_contains_lower = (name_contains or "").lower()
    indices = []
    for idx, d in enumerate(devices):
        if kind == "input" and d["max_input_channels"] > 0:
            indices.append((idx, d))
        elif kind == "output" and d["max_output_channels"] > 0:
            indices.append((idx, d))
    for idx, d in indices:
        if name_contains_lower and name_contains_lower in d["name"].lower():
            return idx
    return None

def configure_audio_devices():
    """Configure explicit input/output devices by name (if provided in .env)."""
    in_name = os.getenv("INPUT_DEVICE_NAME")
    out_name = os.getenv("OUTPUT_DEVICE_NAME")

    try:
        if out_name:
            out_idx = pick_device_index(out_name, "output")
            if out_idx is not None:
                sd.default.device = (sd.default.device[0], out_idx)
                console.print(f"[green]✓ Speaker:[/green] {sd.query_devices(out_idx)['name']}")
            else:
                console.print(f"[yellow]⚠ Output device not found:[/yellow] {out_name}. Using default.")
        else:
            devices = sd.query_devices()
            default_out = sd.default.device[1]
            console.print(f"[green]✓ Speaker:[/green] {devices[default_out]['name']}")

        if in_name:
            in_idx = pick_device_index(in_name, "input")
            if in_idx is not None:
                sd.default.device = (in_idx, sd.default.device[1])
                console.print(f"[green]✓ Microphone:[/green] {sd.query_devices(in_idx)['name']}")
            else:
                console.print(f"[yellow]⚠ Input device not found:[/yellow] {in_name}. Using default.")
        else:
            devices = sd.query_devices()
            default_in = sd.default.device[0]
            console.print(f"[green]✓ Microphone:[/green] {devices[default_in]['name']}")
    except Exception as e:
        console.print(f"[red]Audio device configuration failed:[/red] {e}")
        sys.exit(1)

def normalize_intent(text: str) -> str:
    """Normalize user text for intent checks: lowercase, strip whitespace/punctuation."""
    t = text.lower().strip()
    t = re.sub(r"[^\w\s]", "", t)
    return t

def log_user(text: str):
    console.print(f"[yellow]You:[/yellow] {text}")

def log_ai(text: str):
    console.print(f"[blue]Sapience:[/blue] {text}")

def log_info(msg: str):
    console.print(f"[cyan]{msg}[/cyan]")

def log_error(msg: str):
    console.print(f"[red]{msg}[/red]")

def retry_with_backoff(func):
    """Retry API calls with exponential backoff on failure."""
    def wrapper(*args, **kwargs):
        max_retries = 5
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                wait = (2 ** attempt) + random.uniform(0, 0.75)
                console.print(f"[red]Error:[/red] {e} — retrying in {wait:.2f}s")
                time.sleep(wait)
    return wrapper