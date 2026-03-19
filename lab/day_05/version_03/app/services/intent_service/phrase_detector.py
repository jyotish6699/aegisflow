from .patterns import INTENT_PATTERNS

def detect_phrase_intents(message: str):

    phrase_intent_weight = 1.5 # phase weight is less important than role weight 
    scores = {}

    for intent, patterns in INTENT_PATTERNS.items():
        for phrase in patterns:
            words = phrase.split()

            # check if all words exist in message
            if all(word in message for word in words):
                scores[intent] = scores.get(intent, 0) + phrase_intent_weight

    return scores