from fastapi import FastAPI
from pydantic import BaseModel
import time

from intent.classifier import classify_intent
from behavior.tracker import track_event
from response.generator import generate_response

app = FastAPI()

class IntentRequest(BaseModel):
    user_id: str
    text: str

@app.post("/intent")
def receive_intent(req: IntentRequest):
    intent, confidence = classify_intent(req.text)

    timestamp = time.time()
    behavior_state = track_event(req.user_id, intent, timestamp)
    system_response = generate_response(intent, behavior_state)

    return {
        "intent_event": {
            "user_id": req.user_id,
            "raw_text": req.text,
            "intent": intent,
            "confidence": confidence,
            "timestamp": timestamp
        },
        "system_response": system_response
    }
