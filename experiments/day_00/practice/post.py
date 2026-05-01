from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

def intent_handler(text: str):
    text = text.lower()
    if "help" in text:
        return "help", 0.9
    if "motivation" in text:
        return "motivation", 0.8
    if "guidance" in text:
        return "guidance", 0.2
    if "roadmap" in text:
        return "roadmap", 0.5
    
def system_response(text: str):
    text = text.lower()
    if "help" in text:
        return "i will help."
    if "motivation" in text:
        return "i will motivate you."
    if "guidance" in text:
        return "i will guide you."
    if "roadmap" in text:
        return "i will give you roadmap"

class IntentRequest(BaseModel):
    user_id: str
    text: str

class User(BaseModel):
    name: str
    college: str
    semester: int

@app.post("/user/intent")
async def Intent_handler(req: IntentRequest):
    print(req)
    intent, confidence = intent_handler(req.text)
    system_respond = system_response(req.text)

    return {
        "intent_event": {
            "user_id": req.user_id,
            "raw_text": req.text,
            "intent": intent,
            "confidence": confidence
        },
        "system_response": system_respond
    }

@app.post("/user")
async def handler(user: User):
    print(user)
    return user


# @app.post("/")
# async def request_handler(request: Request):
#     body = await request.json()
#     print(body)
#     return body