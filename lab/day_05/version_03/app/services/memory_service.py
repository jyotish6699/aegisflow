from app.storage.redis_store import redis_store

class MemoryService:

    def get(self, user_id: str):
        return {
            "meta": redis_store.get_meta(user_id),
            "intent_freq": redis_store.get_intent_freq(user_id),
            "recent_intents": redis_store.get_recent_intents(user_id),
            "recent_behavior": redis_store.get_recent_behavior(user_id),
            "prediction": redis_store.get_prediction(user_id),
            "recent_prediction": redis_store.get_recent_prediction(user_id)
        }

    def init_state(self, user_id: str):
        if not redis_store.get_meta(user_id):
            redis_store.set_meta(user_id,{
                "user_id": user_id,
                "total_events": 0
            })

        return self.get(user_id)

    def update_intent(self, user_id: str, event: dict):
        intent = event["intent"]

        redis_store.increment_intent(user_id, intent)
        redis_store.push_recent_intent(user_id, intent)

        meta  = redis_store.get_meta(user_id)
        total = int(meta.get("total_events", 0)) + 1

        redis_store.set_meta(user_id, {
            "total_events": total
        })


        return self.get(user_id)
    
    def update_behavior(self, user_id: str, behavior: dict):
        redis_store.set_behavior(user_id, behavior)

        # store behavior history (mode only)
        if "mode" in behavior:
            redis_store.push_recent_behavior(user_id, behavior["mode"])

    def update_prediction(self, user_id: str, prediction: dict):
        redis_store.set_prediction(user_id, prediction)

        if prediction.get("next_intent"):
            redis_store.push_recent_prediction(
                user_id,
                prediction["next_intent"]
            )

    def save(self, user_id: str, state: dict):
        """
        Optional:

        In Redis-native design, most updates already happen step-by-step

        Use only if:
        - syncing derived fields
        - or fallback persistence

        Otherwise can be NO-OP
        """
        pass


memory_service = MemoryService()