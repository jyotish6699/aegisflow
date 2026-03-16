def detect_help_role(tokens):
    if "help" not in tokens:
        return None
    
    if "me" in tokens:
        return "request_help"
    
    if "you" in tokens and "i" in tokens:
        return "offer_help"
    
    return None