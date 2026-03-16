from .preprocessing import preprocess
from .phrase_detector import detect_phrase_intents
from .role_detector import detect_help_role
from .negation_handler import detect_negation
from .scorer import choose_intent

def intent_extraction(user_id: str, text: str) -> list[str]:

    message, tokens = preprocess(text)

    scores = {}

    # phrase rule
    phrase_scores = detect_phrase_intents(message)

    for k, v in phrase_scores.items():
        scores[k] = scores.get(k, 0) + v

    # role rule
    role_intent = detect_help_role(tokens)

    if role_intent:
        scores[role_intent] = scores.get(role_intent, 0) + 2

    # negation rule
    if detect_negation(tokens):
        if "request_help" in scores:
            del scores["request_help"]

    final_intent = choose_intent(scores)

    if final_intent:
        return [final_intent]
    
    return []