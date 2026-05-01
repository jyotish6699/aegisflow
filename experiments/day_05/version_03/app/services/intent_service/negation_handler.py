NEGATIONS = ["no", "not", "dont", "don't", "never", "nahh"]

def detect_negation(tokens):

    for word in tokens:
        if word in NEGATIONS:
            return True
        
    return False