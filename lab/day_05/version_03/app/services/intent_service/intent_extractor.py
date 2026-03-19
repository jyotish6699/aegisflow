from datetime import datetime

from .preprocessing import preprocess
from .phrase_detector import detect_phrase_intents
from .role_detector import detect_help_role
from .negation_handler import detect_negation
from .score_give import choose_intent

def intent_extraction(text: str) -> list[str]:

    message, tokens = preprocess(text)

    # now scores is a global score for all source 
    scores = {}

    # phrase rule
    phrase_scores = detect_phrase_intents(message)
    #return phrase_scores    

    for k, v in phrase_scores.items():
        scores[k] = scores.get(k, 0) + v


    # role rule
    role_intent = detect_help_role(tokens)

    # role based intent is most important than phase intent because two source of truth for one intent
    ROLE_WEIGHT = 2
    if role_intent:
        scores[role_intent] = scores.get(role_intent, 0) + ROLE_WEIGHT

    # negation rule
    NEGATION_PENALTY = 0.5   

    if detect_negation(tokens):
        if "request_help" in scores:
            scores["request_help"] *= NEGATION_PENALTY

    final_intent = choose_intent(scores)

    if final_intent:
        return [final_intent]
    
    return []


def build_event(user_id, text):
    intents = intent_extraction( text)

    if not intents:
        return None
    
    return {
        "user_id": user_id,
        "intent": intents[0],
        'timestamp': datetime.utcnow().isoformat()
    }


print(intent_extraction("i need roadmap"))