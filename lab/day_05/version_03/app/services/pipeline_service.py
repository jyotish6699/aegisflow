from app.services.intent_service.intent_extractor import build_event

class PipelineService:

    def run(self, user_id: str, text: str):
        
        # STEP 1: Build event(intent extraction inside)
        event = build_event(user_id, text)

        if not event:
            return {
                "status": "no_intent_detected",
                "input": text
            }
        

        # STEP 3: return structured response
        return {
            "status": "success",
            "event": event
        }
        
    
# Singleton instance
pipeline = PipelineService()

def get_pipeline_service():
    return pipeline