from fastapi import FastAPI
from pydantic import BaseModel
import redis
import json

app = FastAPI()

# connect to redis
r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True # so it returns string not bytes
)

# intent_extraction
def intent_extraction(user_id: str, text: str) -> list[str]:
    raw_text = text.lower()
    detected_intents = []

    intent_match = {
        "help":["help","confused", "assist", "support"],
        "motivation":["motivation", "inspire", "encourage"],
        "guidance": ["guide", "assist", "mentor"]
    }

    for intent, patterns in intent_match.items():
        for p in patterns:
            if p in raw_text:
                detected_intents.append(intent)

    return detected_intents

    

# MANAGER using Redis
def manager(user_id: str, text: str):

    detected_intents = intent_extraction(user_id, text)

    key = f"user:{user_id}"

    old_data = r.get(key)

    if old_data:
        memory = json.loads(old_data)
    else:
        memory = {
            "total_events": 0,
            "event_index": 0,
            "last_intent": None,
            "intent_freq": {},
            "event_log": [],
            "dominant_intent": None,
            "confidence_score": None
        }

    # Update counters
    memory["total_events"] += 1
    memory["event_index"] += 1

    # Update intent frequency
    for intent in detected_intents:
        memory["intent_freq"][intent] = (
            memory["intent_freq"].get(intent, 0) + 1
        )
        memory["last_intent"] = intent

    # Create event object
    event_obj = {
        "event_index": memory["event_index"],
        "intents": [
            {"intent": intent, "intent_index": i}
            for i, intent in enumerate(detected_intents)
        ]
    }

    memory["event_log"].append(event_obj)

    # Save back to Redis
    r.set(key, json.dumps(memory))

    return memory

def confidence(user_id: str):
    key = f"user:{user_id}"
    old_data = r.get(key)

    if not old_data:
        return None

    user_memory = json.loads(old_data)

    total_events = user_memory.get("total_events", 0)
    intent_freq = user_memory.get("intent_freq", {})

    if total_events == 0 or not intent_freq:
        return 0.0
    
    dominant_intent = max(intent_freq, key=intent_freq.get)
    dominant_count = intent_freq[dominant_intent]

    confidence_score = dominant_count / total_events

    # update memory
    user_memory["dominant_intent"] = dominant_intent

    if total_events < 3:
        user_memory["confidence_score"] = "building"
        r.set(key, json.dumps(user_memory))

        return "building"

    user_memory["confidence_score"] = round(confidence_score, 2)
    
    r.set(key, json.dumps(user_memory))

    return user_memory["confidence_score"]



# api schema 
class intentEvent(BaseModel):
    user_id: str
    text: str

# api endpoint handler(decorator)
@app.post("/user/intent")
async def Api_handler(req: intentEvent):

    updated_memory = manager(req.user_id, req.text)
    confidence_score = confidence(req.user_id)
    
    return {
        "payload": {
            "user_id": req.user_id,
            "raw_text": req.text,
            "confidence": confidence_score,
            "memory": updated_memory
        }
    }


@app.get("/user/{user_id}/memory")
def memory_read(user_id: str):
    key = f"user:{user_id}"
    old_data = r.get(key)

    if not old_data:
        return {"message": "no memory found"}
    else:
        return json.loads(old_data)
    