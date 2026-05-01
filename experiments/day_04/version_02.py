from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import psycopg2
import redis
import json

app = FastAPI()

# connect to redis
r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True  # so it returns string not bytes
)

conn = psycopg2.connect(
    host = "localhost",
    database = "aegisflow",
    user = "jyotish",
    password = "1234", 
    port = 5432
)

cursor = conn.cursor()

def store_event(user_id, text, intents):

    query = """
    INSERT INTO user_events (user_id, raw_text, intents, created_at)
    VALUES (%s, %s, %s, %s)
    """

    cursor.execute(query, (user_id, text, intents, datetime.utcnow()))

    conn.commit()

def intent_extraction(user_id: str, text: str) -> list[str]:
    message = text.lower()
    tokens = message.split()

    intent_detection = []

    INTENTS = {
        "help": ["help", "confused", "assist", "support"],
        "motivation": ["motivation", "inspire", "encourage"],
        "guidance": ["guidance", "guide", "assist", "mentor"],
        "roadmap": ["roadmap", "notes"]
    }

    for intent, patterns in INTENTS.items():
        for p in patterns:
            if p in tokens:
                intent_detection.append(intent)

    return intent_detection


def memory_manager(user_id: str, text: str):

    detected_intents = intent_extraction(user_id, text)

    key = f"user:{user_id}"
    old_data = r.get(key)
     
    if old_data:
        user_memory = json.loads(old_data)
    else:
        user_memory = {
            "meta": {
                "total_events": 0,
                "last_event_time": None,
                "user_stage": None
            },
            "intent": {
                "last_intent": None,
                "dominant_intent": None,
                "intent_freq": {},
                "intent_score": {},
                "recent_intents": [],
                "streak": {
                    "intent": None,
                    "count": 0
                },
                "transition_graph": {}
            },
            "confidence": {}
        }
    
    # META UPDATE
    user_meta = user_memory["meta"]
    current_time = datetime.utcnow().isoformat()

    user_meta["total_events"] += 1
    user_meta["last_event_time"] = current_time

    
    user_intent = user_memory["intent"]

    if detected_intents:

        # intent transition graph
        transition = user_intent.get("transition_graph", {})
        previous_intent = user_intent.get("last_intent")

        if previous_intent:
            prev = previous_intent[0]
            curr = detected_intents[0]

            if prev not in transition:
                transition[prev] = {}

            transition[prev][curr] = transition[prev].get(curr, 0) + 1

        user_intent["transition_graph"] = transition

        # INTENT UPDATE 
        user_intent["last_intent"] = detected_intents

        # user stage update
        if user_meta["total_events"] == 1:
            user_meta["user_stage"] = "new_user"
        elif 2 <= user_meta["total_events"] <=5:
            user_meta["user_stage"] = "active_user"
        else:
            user_meta["user_stage"] = "power_user"

        scores = user_intent.get("intent_score", {})

        for i in detected_intents:
            # update frequency
            freq = user_intent["intent_freq"]
            freq[i] = freq.get(i, 0) + 1

            # decay old intents
            for key in scores:
                scores[key] *= 0.9
            
            # boost new intent
            scores[i] = scores.get(i, 0) + 1

            user_intent["intent_score"] = scores

            # Update recent window(max 5)
            recent = user_intent["recent_intents"]
            recent.append(i)
            if len(recent) > 5:
                recent.pop(0)
            
            # update streak
            streak = user_intent["streak"]
            if streak["intent"] == i:
                streak["count"] += 1
            else:
                if streak["count"] > 2:
                    # strong streak broken
                    streak["intent"] = i
                    streak["count"] = 1
                else:
                    # weak streak replaced
                    streak["intent"] = i
                    streak["count"] = 1

        # update dominant
        if scores:
            dominant = max(scores, key=scores.get)
            user_intent["dominant_intent"] = dominant

    r.set(key, json.dumps(user_memory))

    return user_memory



def behavior_engine(user_memory):
    intent = user_memory["intent"]
    meta = user_memory["meta"]

    dominant = intent["dominant_intent"]
    streak = intent["streak"]["count"]

    behavior = None

    if dominant == "help" and streak >= 3:
        behavior = "user_struggling"
    elif dominant == "roadmap" and meta["total_events"] > 5:
        behavior = "goal_oriented"
    elif dominant == "motivation":
        behavior = "needs_encouragement"

    return behavior


def decision_engine(behavior):
    if behavior == "user_struggling":
        return "offer_guidance"
    
    if behavior == "goal_oriented":
        return "suggest_roadmap"
    
    if behavior == "needs_encouragement":
        return "send_response"
    
    return "normal_response"


def predict_next_intent(user_intent):

    graph = user_intent.get("transition_graph", {})
    last = user_intent.get("last_intent")

    if not last:
        return None, 0
    
    last = last[0]

    if last not in graph:
        return None, 0
    
    total = sum(graph[last].values())
    next_intent = max(graph[last], key=graph[last].get)

    confidence = graph[last][next_intent] / total

    return next_intent, confidence


    

class RequestSchema(BaseModel):
    user_id: str
    text: str

@app.post("/user/intent")
def handler_api_endpoint(req: RequestSchema):

    detected_intents = intent_extraction(req.user_id, req.text)

    store_event(req.user_id, req.text, detected_intents)

    user_memory = memory_manager(req.user_id, req.text)
    prediction, confidence = predict_next_intent(user_memory["intent"])

    behavior = behavior_engine(user_memory)

    decision = decision_engine(behavior)


    return {
        "payload": {
            "user_id": req.user_id,
            "raw_text": req.text
        },
        "prediction": prediction,
        "confidence": confidence,
        "behavior": behavior,
        "decision": decision,
        "user_memory": user_memory
    }


@app.get("/health")
def health():
    return {"status": "ok"}

