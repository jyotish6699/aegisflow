def intent_handler(text: str):
    message = text.lower()
    if "help" in message:
        return "help"
    if "motivation" in message:
        return "motivation"
    if "guidance" in message:
        return "guidance"
    if "roadmap" in message:
        return "roadmap"