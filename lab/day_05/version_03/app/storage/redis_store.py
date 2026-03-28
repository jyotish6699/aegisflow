import redis

class RedisStore:
    def __init__(self):
        self.r = redis.Redis(
            host="localhost",
            port=6379,
            decode_responses=True
        )

    # -------- META (HASH) --------
    def get_meta(self, user_id):
        return self.r.hgetall(f"user:{user_id}:meta")

    def set_meta(self, user_id, data: dict):
        key = f"user:{user_id}:meta"
        self.r.hset(key, mapping=data)
        self.r.expire(key, 3600)

    # -------- INTENT FREQ (HASH) --------
    def get_intent_freq(self, user_id):
        return self.r.hgetall(f"user:{user_id}:intent_freq")

    def increment_intent(self, user_id, intent):
        key = f"user:{user_id}:intent_freq"
        self.r.hincrby(key, intent, 1)
        self.r.expire(key, 3600)


    # -------- RECENT INTENTS (LIST) --------
    def push_recent_intent(self, user_id, intent):
        key = f"user:{user_id}:recent_intents"
        self.r.lpush(key, intent)
        self.r.ltrim(key, 0, 9)
        self.r.expire(key, 3600)

    def get_recent_intents(self, user_id):
        return self.r.lrange(f"user:{user_id}:recent_intents", 0, -1)

    # -------- BEHAVIOR (HASH) --------
    def set_behavior(self, user_id, data: dict):
        key = f"user:{user_id}:behavior"
        self.r.hset(key, mapping = data)
        self.r.expire(key, 3600)

    def get_behavior(self, user_id):
        """HGETALL user:{id}:behavior"""
        return self.r.hgetall(f"user:{user_id}:behavior")

    # ---------- RECENT BEHAVIOR (LIST) ---------
    def push_recent_behavior(self, user_id, behavior_mode):
        key = f"user:{user_id}:recent_behavior"
        self.r.lpush(key, behavior_mode)
        self.r.ltrim(key, 0, 9)
        self.r.expire(key, 3600)

    def get_recent_behavior(self, user_id):
        return self.r.lrange(f"user:{user_id}:recent_behavior", 0, -1)

    # -------- PREDICTION (HASH) --------
    def set_prediction(self, user_id, data: dict):
        """HSET user:{id}:prediction"""
        key = f"user:{user_id}:prediction"
        self.r.hset(key, mapping = data)
        self.r.expire(key, 3600)

    def get_prediction(self, user_id):
        """HGETALL user:{id}:prediction"""
        return self.r.hgetall(f"user:{user_id}:prediction")
    
    # ------ RECENT PREDICTION (LIST) --------
    def push_recent_prediction(self, user_id, prediction):
        key = f"user:{user_id}:recent_prediction"
        self.r.lpush(key, prediction)
        self.r.ltrim(key, 0, 9)
        self.r.expire(key, 3600)

    def get_recent_prediction(self, user_id):
        return self.r.lrange(f"user:{user_id}:recent_prediction", 0, -1)


redis_store = RedisStore()




