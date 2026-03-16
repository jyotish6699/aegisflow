from .patterns import INTENT_PATTERNS

def detect_phrase_intents(message: str):

    intents = []
    scores = {}

    for intent, patterns in INTENT_PATTERNS.items():
        for phrase in patterns:
            if phrase in message:
                scores[intent] = scores.get(intent, 0) + 1

    return scores