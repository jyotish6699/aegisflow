# Pydantic base class
from pydantic import BaseModel

# UUID type
from uuid import UUID

# Python datetime
from datetime import datetime


# -------------------------------------------------
# Event Create Schema
# -------------------------------------------------
# Request body received from the frontend.

class EventCreate(BaseModel):

    # Session to which this event belongs
    session_id: UUID

    # Type of event
    event_type: str

    # Time when the event occurred
    occurred_at: datetime

    # Event-specific data
    payload: dict


# -------------------------------------------------
# Event Response Schema
# -------------------------------------------------
# Response returned by the backend after storing an event.

class EventResponse(BaseModel):

    id: UUID

    session_id: UUID

    event_type: str

    occurred_at: datetime

    payload: dict

    created_at: datetime

    model_config = {
        "from_attributes": True
    }