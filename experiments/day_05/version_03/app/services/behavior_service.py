class BehaviorService:

    def update(self, state: dict):

        freq = {k: int(v) for k,v in state.get("intent_freq", {}).items()}
        recent = state.get("recent_intents", [])
        total = int(state.get("meta", {}).get("total_events", 0))

        behavior = {}

        # FOCUS
        if len(set(recent)) == 1:
            behavior["mode"] = "focused"
        elif len(set(recent)) >= 4:
            behavior["mode"] = "exploring"
        else:
            behavior["mode"] = "normal"
        
        # HABIT 
        if freq:
            top = max(freq, key=freq.get)
            if freq[top] / max(total, 1) > 0.6:
                behavior["pattern"] = "habitual"

        # ENGAGEMENT
        if total > 50:
            behavior["engagement"] = "high"
        elif total < 5:
            behavior["engagement"] = "low"
        else:
            behavior["engagement"] = "medium"

        state["behavior"] = behavior

        return state, behavior
        


behavior_service = BehaviorService()