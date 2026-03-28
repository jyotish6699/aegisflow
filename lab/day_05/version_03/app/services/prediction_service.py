class PredictionService:
    
    def update(self, state: dict):

        freq = {k: int(v) for k, v in state.get("intent_freq, {}").items()}
        recent = state.get("recent_intents", []) 
        recent_behavior = state.get("recent_behavior", [])

        prediction = {
            "next_intent": None,
            "confidence": 0.0,
            "type": None
        }       

        # ------- 1. RECENT PATTERN (STRONG SIGNAL) ----------
        if len(recent) >= 3:
            if len(set(recent[:3])) == 1:
                # last 3 same
                prediction["next_intent"] = recent[0]
                prediction["confidence"] = 0.8
                prediction["type"] = "momentum"
                return self._attach(state, prediction)
            
        # ------- 2. FREQUENCY (LONG TERM) ------    
        if freq:
            top_intent = max(freq, key=freq.get)
            prediction["next_intent"] = top_intent
            prediction["confidence"] =  0.6
            prediction["type"] = "habit"

        # ----- 3. BEHAVIOR BASED ADJUSTMENT --------
        if recent_behavior:
            last_mode = recent_behavior[0]
            
            if last_mode == "exploring":
                prediction["confidence"] -= 0.2
                prediction["type"] = "uncertain"

            elif last_mode == "focused":
                prediction["confidence"] += 0.1

        return self._attach(state, prediction)
    
    def _attach(self, state, prediction):
        state["prediction"] = prediction
        return state, prediction

prediction_service = PredictionService()