from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db

from services.event_service import save_event

from schemas.event import EventCreate, EventResponse

from validators.event_validator import validate_event

from services.session_validation_service import validate_session_reference


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

    event_data = event.model_dump()

    validate_event(event_data)

    validate_session_reference(
        db=db,
        session_id=event_data["session_id"],
    )

    saved_event = save_event(
        db=db,
        event_data=event_data,
    )

    return saved_event