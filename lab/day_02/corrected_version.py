from fastapi import FastAPI
from pydantic import BaseModel
from day_02.intent_extraction import intent_extraction
from typing import Dict, Any, List

app = FastAPI()

# -----------------------------
# Global in-memory store
# -----------------------------
user_memory: Dict[str, Dict[str, Any]] = {}


# -----------------------------
# Utility functions
# -----------------------------

def base_confidence_score(text: str) -> float:
    """
    Event-level confidence from language strength only.
    """
    strong_words = ["need", "help", "urgent", "confused", "stuck"]
    score = 0.5  # baseline

    for word in strong_words:
        if word in text:
            score += 0.1

    return min(score, 0.85)


def recency_bias(user: Dict[str, Any], intent: str) -> float:
    """
    Event-index based recency decay.
    Skips current event to avoid always returning 1.0.
    """
    current_index = user["event_index"]

    # Skip the current event (last one)
    for event in reversed(user["event_log"][:-1]):
        for item in event["intents"]:
            if item["intent"] == intent:
                gap = current_index - event["event_index"]
                return 1 / (1 + gap)

    return 0.0


# -----------------------------
# Core manager
# -----------------------------

def manager(user_id: str, text: str) -> Dict[str, Any]:
    text = text.lower()
    intents: List[str] = intent_extraction(text)

    # Initialize user state
    if user_id not in user_memory:
        user_memory[user_id] = {
            "total_events": 0,
            "event_index": 0,
            "intent_freq": {},
            "last_intent": None,
            "event_log": []
        }

    user = user_memory[user_id]

    # -----------------------------
    # Event-level updates
    # -----------------------------
    user["event_index"] += 1
    user["total_events"] += 1

    event = {
        "event_index": user["event_index"],
        "intents": []
    }

    for idx, intent in enumerate(intents):
        event["intents"].append({
            "intent": intent,
            "intent_index": idx
        })

    user["event_log"].append(event)

    # -----------------------------
    # Update intent frequency
    # -----------------------------
    for intent in intents:
        freq = user["intent_freq"]
        freq[intent] = freq.get(intent, 0) + 1

    # -----------------------------
    # Dominant intent (simple rule)
    # -----------------------------
    dominant_intent = intents[0] if intents else None
    user["last_intent"] = dominant_intent

    # -----------------------------
    # Metric derivation
    # -----------------------------
    intent_freq = user["intent_freq"]
    total_intents = sum(intent_freq.values())

    # Intent strength
    intent_strength = (
        intent_freq.get(dominant_intent, 0) / total_intents
        if total_intents > 0 and dominant_intent else 0
    )

    # Diversity (dominant ratio)
    dominant_ratio = (
        max(intent_freq.values()) / total_intents
        if total_intents > 0 else 0
    )

    # Base confidence
    base_conf = base_confidence_score(text)

    # Recency bias
    recency = (
        recency_bias(user, dominant_intent)
        if dominant_intent else 0
    )

    # -----------------------------
    # Final confidence
    # -----------------------------
    confidence = (
        0.4 * base_conf +
        0.3 * intent_strength +
        0.2 * recency +
        0.1 * dominant_ratio
    )

    confidence = min(max(confidence, 0.0), 1.0)

    return {
        "dominant_intent": dominant_intent,
        "confidence": confidence,
        "metrics": {
            "base_confidence": base_conf,
            "intent_strength": intent_strength,
            "recency_bias": recency,
            "diversity_penalty": dominant_ratio
        }
    }


# -----------------------------
# API Schema
# -----------------------------

class IntentEvent(BaseModel):
    user_id: str
    text: str


# -----------------------------
# API Endpoint
# -----------------------------

@app.post("/user/intent")
async def url_handler(req: IntentEvent):
    result = manager(req.user_id, req.text)

    return {
        "user_intent": {
            "user_id": req.user_id,
            "raw_text": req.text,
            "intent": result["dominant_intent"],
            "confidence": result["confidence"],
            "debug": result["metrics"]
        }
    }
