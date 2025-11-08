reply = generate_response(user_text)

# Awareness: only recall if the user mentions something already in profile
if profile.get("interests"):
    for interest in profile["interests"]:
        if interest.lower() in user_text.lower():
            # Subtle acknowledgement
            reply += f" Yes, I remember you mentioned that before."
            break

log_ai(reply)
speak_text(reply)