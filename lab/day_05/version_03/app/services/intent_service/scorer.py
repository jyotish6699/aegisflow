def choose_intent(scores):

    if not scores:
        return None
    
    return max(scores, key=scores.get)

