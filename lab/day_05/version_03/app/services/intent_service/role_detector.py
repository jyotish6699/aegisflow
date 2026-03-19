def detect_help_role(tokens):
    help_words = {"help", "assist", "support", "guide"}
    if not any(word in tokens for word in help_words):
        return None
    
    # offer help(i help you)
    if "i" in tokens and "you" in tokens:
        return "offer_help"
    
    # request help(you help me)
    if "me" in tokens:
        return "request_help"
    
    return None