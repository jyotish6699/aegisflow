from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


# =====================================================
# Timeline Event
# =====================================================

class TimelineEvent(BaseModel):

    id: UUID

    event_type: str

    occurred_at: datetime

    payload: dict

    model_config = {
        "from_attributes": True
    }


# =====================================================
# Timeline
# =====================================================

class Timeline(BaseModel):

    session_id: UUID

    started_at: datetime

    ended_at: datetime | None

    events: list[TimelineEvent]

    model_config = {
        "from_attributes": True
    }