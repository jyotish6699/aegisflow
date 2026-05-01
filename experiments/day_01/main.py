from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

def intent_handler(text: str):
    message = text.lower()
    if "help" in message:
        return "help"
    if "motivation" in message:
        return "motivation"
    if "guidance" in message:
        return "guidance"
    if "roadmap" in message:
        return "roadmap"

user_memory: dict[str, dict[str]] = {}

def generate_confidence(user_id: str, text: str):
    intent_text = intent_handler(text)

    base_confidence = 0.5
    alpha = 0.4

    if user_id not in user_memory:
        user_memory[user_id] = []

        return base_confidence


    user_memory[user_id].append(intent_text)
    user_id = user_memory.get(user_id)
    no_of_past_intent = len(user_id)


    intent_strength = 1/no_of_past_intent
    confidence = base_confidence + alpha * intent_strength
    return min(confidence, 0.95)

    


class UserIntent(BaseModel):
    user_id: str
    text: str

@app.post("/user/intent")
async def request_handler(req: UserIntent):
    print(req)

    intent = intent_handler(req.text)
    confidence = generate_confidence(req.user_id, req.text)

    return {
        "user_intent": {
            "user_id": req.user_id,
            "raw_text": req.text,
            "intent": intent,
            "confidence": confidence,
            "memory_stats": {
                "total_events": 4,
                "intent_frequency": 2
            }
            
        }
    }