# ADD RELATIVE CONFIDENCE CHECK

def choose_intent(scores):
    if not scores:
        return "unknown"
    
    # this line converts dic into x=(key, value) tuples pairs and sorts them by value(score) in descending order so you can pick the strongest intent with value in list of tuples 
    # sorted_intents return list of tuples in des order
    
    sorted_intents = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    best, best_score = sorted_intents[0]

    # absoulte threshold
    if best_score < 1.5:
        if best_score > 0:
            return best   # weak but still useful
        return "uncertain"
    
    # relative threshold (difference check)
    if len(sorted_intents) > 1:
        second_score = sorted_intents[1][1]
        if best_score - second_score < 0.3:
            return "uncertain"
        
    return best




# THIS IS TOO RISKY WHEN RELATIVE THRESHOLD

# def choose_intent(scores):

#     if not scores:
#         return None
    
#     best = max(scores, key=scores.get)

#     if scores[best] < 1.5:
#         return "uncertain"
    
#     return best
    

