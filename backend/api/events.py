from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from services.event_service import save_event

from schemas.event import EventCreate

router = APIRouter()

@router.post("/events")
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    
    saved_event = save_event(db, event.model_dump())

    return {
        "status": "success",
        "event_id": str(saved_event.event_id)
    }