# PURE API LAYER
# Only handles request/response + dependency injection does not contain logic anymore

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel


from app.services.pipeline_service import get_pipeline_service, PipelineService

router = APIRouter()
    
# Request Schema
class IntentRequest(BaseModel):
    user_id: str
    text: str

# Response Schema
class IntentResponse(BaseModel):
    result: dict


# Route
@router.post("/intent", response_model=IntentResponse)
def handle_intent(
    request: IntentRequest,
    debug: bool = Query(False, description="Enable debug mode"),
    pipeline: PipelineService = Depends(get_pipeline_service)
):
    try:
        # NO BUSINESS LOGIC HERE
        result = pipeline.run(
            user_id=request.user_id,
            text=request.text,
            debug = debug
        )

        return IntentResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    