user_memory = {
    "user123": {
        "total_events": 0,
        "event_index": 0,
        "last_intent": None,
        "intent_freq": {},
        "event_log": []
    }
}

# def update_user_memory(user_id: str, intents: list[str]):
#     if user_id not in user_memory:
#         user_memory[user_id] = {}



# EXAMPLE

# {
#   "total_events": 1,
#   "event_index": 1,
#   "last_intent": "help",
#   "intent_freq": {
#     "help": 1,
#     "guidance": 1
#   },
#   "event_log": [
#     {
#       "event_index": 1,
#       "intents": [
#         { "intent": "help", "intent_index": 0 },
#         { "intent": "guidance", "intent_index": 1 }
#       ]
#     }
#   ]
# }
