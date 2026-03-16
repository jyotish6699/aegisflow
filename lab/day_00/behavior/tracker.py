user_state = {}

def track_event(user_id: str, intent: str, timestamp: float):
    state = user_state.get(user_id, {"count": 0})
    state["count"] += 1
    state["last_intent"] = intent
    state["last_seen"] = timestamp
    user_state[user_id] = state
    return state

# user_state = {}

# def track_event(user_id: str, intent: str, timestamp: float):
#     state = user_state.get(user_id, {"count": 0})
#     state["count"] +=1
#     state["last_intent"] = intent
#     state["last_seen"] = timestamp
#     user_state[user_id] = state
#     return state