"""
Global configuration for Sapience.
"""

# ElevenLabs
ELEVEN_VOICE_ID = "MhpxdyQAdWhJC6ixJfYo"  # replace if needed

# LLM
USE_LLM_FALLBACK = True
LLM_MODEL = "gpt-4o-mini"
LLM_MAX_TOKENS = 350
LLM_TEMPERATURE = 0.2

# Speaker identification
ENABLE_SPEAKER_ID = True
SPEAKER_SIMILARITY_THRESHOLD = 0.82  # cosine similarity for voice match (0..1)

# Persistence files
STORE_DIR = "data"
SPEAKERS_FILE = f"{STORE_DIR}/speakers.json"     # {name: {"embedding": [...], "facts": [...], "history": [...]}}
GLOBAL_FILE   = f"{STORE_DIR}/global.json"       # {"facts": [...], "history": [...]}
TRANSCRIPTS   = f"{STORE_DIR}/transcripts.jsonl" # streaming log of interactions

# Chat behavior
MAX_HISTORY_PER_SPEAKER = 20
SYSTEM_PERSONA = (
    "You are Sapience—concise, warm, and factual. "
    "Personalize replies using known speaker preferences. "
    "Call local tools when needed for deterministic info."
)