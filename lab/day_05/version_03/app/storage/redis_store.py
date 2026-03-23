class RedisStore:

    # -------- META (HASH) --------
    def get_meta(self, user_id):
        """HGETALL user:{id}:meta"""
        pass

    def set_meta(self, user_id, data: dict):
        """HSET user:{id}:meta"""
        pass

    # -------- INTENT FREQ (HASH) --------
    def get_intent_freq(self, user_id):
        """HGETALL user:{id}:intent_freq"""
        pass

    def increment_intent(self, user_id, intent):
        """HINCRBY user:{id}:intent_freq intent 1"""
        pass

    # -------- RECENT INTENTS (LIST) --------
    def push_recent_intent(self, user_id, intent):
        """
        LPUSH user:{id}:recent_intents
        LTRIM to fixed size (e.g. last 10)
        """
        pass

    def get_recent_intents(self, user_id):
        """LRANGE user:{id}:recent_intents 0 -1"""
        pass

    # -------- BEHAVIOR (HASH) --------
    def set_behavior(self, user_id, data: dict):
        """HSET user:{id}:behavior"""
        pass

    def get_behavior(self, user_id):
        """HGETALL user:{id}:behavior"""
        pass

    # -------- PREDICTION (HASH) --------
    def set_prediction(self, user_id, data: dict):
        """HSET user:{id}:prediction"""
        pass

    def get_prediction(self, user_id):
        """HGETALL user:{id}:prediction"""
        pass


redis_store = RedisStore()



# ------------- PREVIOUS CODE --------------

# from ..services.intent_service.intent_extractor import build_event
# import redis


# def connect_redis():
#     return redis.Redis(
#         host="localhost",
#         port=6379,
#         decode_responses=True
#     )


# # step1: user exists check
# def user_exists(r, user_id):
#     return r.exists(f"user:{user_id}:meta")

# # step2: create new user memory structure
# def create_user_memory(r, user_id, data):

#     # 1. META
#     r.hset(f"user:{user_id}:meta", mapping={
#         "total_events": 1,
#         "first_event_time": data["timestamp"],
#         "last_event_time": data["timestamp"],
#         "user_stage": "new_user"
#     })

#     # 2. INTENT: FREQ
#     r.hset(f"user:{user_id}:intent:freq", data["intent"], 1)

#     # 3. INTENT:RECENT
#     r.rpush(f"user:{user_id}:intent:recent", data["intent"])
#     print(f"Created memory for {user_id}")

    

# def update_user_memory(r, user_id, event):
#     pass

# def get_user_memory(user_id):
#     pass

# def delete_user_memory(user_id):
#     pass


# # MAIN FLOW
# if __name__ == "__main__":
#     r = connect_redis()

#     event = build_event(user_id = "u101", text= "i need help")

#     if not event:
#         print("No intent detected")
#     else:
#         user_id = event["user_id"]
#         if not user_exists(r, user_id):
#             create_user_memory(r, user_id, event)
#         else:
#             update_user_memory(r, user_id, event)

