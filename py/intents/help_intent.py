def default_reply(user_text: str) -> str:
    """
    Conversational fallback when no intent matches.
    The core logs the unknown phrase and may propose learning.
    """
    return (
        "I’m not sure I understood that. "
        "Try asking for help, the time, my status, or where I am."
    )