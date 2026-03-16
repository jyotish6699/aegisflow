from fastapi import FastAPI
from pydantic import BaseModel
from .intent_extraction import intent_extraction
import math


app = FastAPI()

user_memory: dict[str, dict[str, any]] = {}

def manager(user_id: str, text: str):
    text = text.lower()
    # list of extraction intent 
    intents = intent_extraction(text)

    if user_id not in user_memory:
        user_memory[user_id] = {
            "total_events": 0,
            "event_index": 0,
            "intent_freq": {},
            "last_intent": None,
            "event_log": []
        }

    user_memory[user_id]["event_index"] = user_memory[user_id].get("event_index", 0) + 1
    user_memory[user_id]["total_events"] = user_memory[user_id].get("total_events", 0) + 1

    event = {
        "event_index": user_memory[user_id].get("event_index"),
        "intents": []
    }

    for index, intent in enumerate(intents, start=0):
        event["intents"].append({
            "intent": intent,
            "index": index
        })

    user_memory[user_id]["event_log"].append(event)

    for intent in intents:
        freq = user_memory[user_id]["intent_freq"]
        freq[intent] = freq.get(intent, 0) + 1

    # update last intent 
    user_memory[user_id]["last_intent"] = intents[0] 

    # METRIX DERIVATION
    dominant_intent = user_memory[user_id]["last_intent"]

    #1. intent strength
    intent_freq = user_memory[user_id]["intent_freq"]
    #dominant_intent_count = max(intent_freq.get(i, 0) for i in intents)
    intent_strenth = intent_freq[dominant_intent] / sum(intent_freq.values())

    #2. Diversity calculation
    #unique_intents = len(intent_freq)
    total = sum(intent_freq.values())

    # compute proportions(relative distributions)
    distribution = {}
    for intent, count in intent_freq.items():
        distribution[intent] = count/total

    dominant_ratio = max(distribution.values())

    # normalized entropy
    entropy = 0

    for p in distribution.values():
        entropy -= p * math.log(p)

    #max_entropy = math.log(len(distribution))
    
    #diversity_score = entropy / max_entropy if max_entropy > 0 else 0

    # diversity = {
    #     "unique_intents": len(intent_freq),
    #     "dominant_ratio": max(intent_freq.values()) / sum(intent_freq.values())
    # }

    # confidence calculation
    def base_confidence_score(text: str) -> float:
        strong_words = ["need", 'help', "urgent", "confused", "stuck"]
        score = 0.5 #default baseline 

        for word in strong_words:
            if word in text:
                score += 0.1
        
        return min(score, 0.85)
    

    def recency_bias(user, intent: str) -> float:
        current_index = user["event_index"] 

        for event in reversed(user["event_log"]):
            for item in event["intents"]:
                if item["intent"] == intent:
                    gap = current_index - event["event_index"]
                    return 1 / (1 + gap)
        return 0.0
    

     # base confidence 
    base_conf = base_confidence_score(text)

    # recency bias
    recency = recency_bias(user_memory[user_id], dominant_intent)

    # diversity penalty 
    diversity_penalty = dominant_ratio

    # final confidence 
    confidence = (
        0.4 * base_conf + 
        0.3 * intent_strenth + 
        0.2 * recency + 
        0.1 * diversity_penalty
    )

    confidence = min(max(confidence, 0), 1)


    return {
        "dominant_intent": dominant_intent,
        "confidence": confidence,
        "metrices": {
            "base_confidence": base_conf,
            "intent_strength": intent_strenth,
            "recency_bias": recency,
            "diversity_penalty": diversity_penalty
        }
    }

class IntentEvent(BaseModel):
    user_id: str
    text: str

@app.post("/user/intent")
async def url_handler(req: IntentEvent):
    result = manager(req.user_id, req.text)
    

    return {
        "user_intent": {
            "user_id": req.user_id,
            "raw_text": req.text,
            "intent": result["dominant_intent"],
            "confidence": result["confidence"],
            "debug": result["metrices"]
        }
    }