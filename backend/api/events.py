from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db

from services.event_service import save_event

from schemas.event import EventCreate, EventResponse


router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


@router.post(
    "",
    response_model=EventResponse,
)
def create_event(
    event: EventCreate,
    db: Session = Depends(get_db),
):

    saved_event = save_event(
        db=db,
        event_data=event.model_dump(),
    )

    return saved_event