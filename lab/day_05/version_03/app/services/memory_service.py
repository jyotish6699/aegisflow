class MemoryService:

    def get(self, user_id: str):
        """
        Assemble state from Redis (multiple structures):

        - meta → HASH
        - intent_freq → HASH
        - recent_intents → LIST
        - behavior → HASH
        - prediction → HASH

        Return combined dict (read model only, not stored as JSON)
        """
        pass

    def init_state(self, user_id: str):
        """
        Initialize base Redis structures:

        - create meta hash (user_id, total_events = 0)
        - other structures empty by default

        Return initial assembled state
        """
        pass

    def update_intent(self, user_id: str, event: dict):
        """
        Update Redis directly:

        - HINCRBY intent_freq
        - LPUSH recent_intents (+ LTRIM)
        - update meta.total_events

        DO NOT mutate Python dict only
        → write directly to Redis

        Return updated state (via get)
        """
        pass

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