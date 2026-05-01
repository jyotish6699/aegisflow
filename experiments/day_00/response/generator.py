def generate_response(intent: str, behavior_state: dict):
    if intent == "help":
        return "I see you need help. I will guide you step by step."
    if intent == "confusion":
        if behavior_state["count"] > 3:
            return "You seem stuck repeatedly. Let’s pause and reset."
        return "You seem confused. Let’s slow down and clarify."
    if intent == "demand":
        return "Noted. I am tracking your request."
    return "I am listening. Tell me more."



# def generator_response(intent: str, behavior_state: dict):
#     if intent == "help":
#         return "I see you need help. I will guide you step by step."
#     if intent == "confusion":
#         if behavior_state["count"] > 3:
#             return "You seem stuck repeatedly. Let's pause and reset."
#         return "You seem confused. Let's slow down and clarify."
#     if intent == "demand":
#         return "Noted. I am tracking your request."
#     return "I am listening. Tell me more."