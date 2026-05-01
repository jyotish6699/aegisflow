def classify_intent(text: str):
    t = text.lower()
    if "help" in t:
        return "help", 0.8 # 0.8 is heuristic value
    if "confuse" in t:
        return "confusion", 0.9
    if "want" in t:
        return "demand", 0.7
    return "unknown", 0.3

intent, confidence = classify_intent("i need help")
print(confidence)

