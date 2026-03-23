class BehaviorService:

    def update(self, user_id: str, state: dict, event: dict):
        """
        Read from state (already from Redis):

        Use:
        - intent_freq
        - recent_intents
        - streak (if added later)

        Compute:
        - current_behavior
        - behavior_score

        Store result in Redis:
        → HSET user:{id}:behavior

        Return:
        (updated_state, behavior_dict)
        """
        pass


behavior_service = BehaviorService()