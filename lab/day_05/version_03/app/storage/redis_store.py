from ..services.intent_service.intent_extractor import build_event
import redis


def connect_redis():
    return redis.Redis(
        host="localhost",
        port=6379,
        decode_responses=True
    )


# step1: user exists check
def user_exists(r, user_id):
    return r.exists(f"user:{user_id}:meta")

# step2: create new user memory structure
def create_user_memory(r, user_id, data):

    # 1. META
    r.hset(f"user:{user_id}:meta", mapping={
        "total_events": 1,
        "first_event_time": data["timestamp"],
        "last_event_time": data["timestamp"],
        "user_stage": "new_user"
    })

    # 2. INTENT: FREQ
    r.hset(f"user:{user_id}:intent:freq", data["intent"], 1)

    # 3. INTENT:RECENT
    r.rpush(f"user:{user_id}:intent:recent", data["intent"])
    print(f"Created memory for {user_id}")

    

def update_user_memory(r, user_id, event):
    pass

def get_user_memory(user_id):
    pass

def delete_user_memory(user_id):
    pass


# MAIN FLOW
if __name__ == "__main__":
    r = connect_redis()

    event = build_event(user_id = "u101", text= "i need help")

    if not event:
        print("No intent detected")
    else:
        user_id = event["user_id"]
        if not user_exists(r, user_id):
            create_user_memory(r, user_id, event)
        else:
            update_user_memory(r, user_id, event)

