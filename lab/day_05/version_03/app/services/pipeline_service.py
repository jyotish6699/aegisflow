from app.services.intent_service.intent_extractor import build_event
# IMPORT SERIVCES 
from app.services.memory_service import memory_service
from app.services.behavior_service import behavior_service
from app.services.prediction_service import prediction_service
from app.services. decision_service import decision_service

# STORAGE
from app.storage.postgres_store import postgres_store


class PipelineService:

    def run(self, user_id: str, text: str):
        
        # 1. LOAD MEMORY (Redis -> current state)
        state = memory_service.get(user_id)

        # 2. INITILIZE STATE (first time user) 
        if not state:
            state = memory_service.init_state(user_id)

        # 3. INTENT EXTRACTION(current input) -> EVENT
        event = build_event(user_id, text)

        if not event:
            return {
                "status": "no_intent_detected",
                "input": text
            }

        # 4. UPDATE STATE(intent_level updated inside memory)
        state = memory_service.update_intent(state, event)

        # 5. BEHAVIOR (pattern detection)
        state, behavior = behavior_service.update(state, event)

        # 6. PREDICTION (next intent etc.)
        state = prediction_service.update(state)

        # 7. DECISION
        decision = decision_service.make(state)

        # 8. SAVE STATE (redis)
        memory_service.save(user_id, state)

        # 9. SAVE RAW EVENT (postgreSQL)
        postgres_store.save_event(event)



        return {
            "status": "success",
            "event": event,
            "behavior": behavior,
            "decision": decision,
            "state": state
        }
        
    
# Singleton instance
pipeline = PipelineService()

def get_pipeline_service():
    return pipeline