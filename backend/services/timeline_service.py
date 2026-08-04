from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.session import Session as SessionModel
from models.event import Event

from schemas.timeline import (
    Timeline,
    TimelineEvent,
)


# =====================================================
# Build Timeline
# =====================================================

def build_timeline(
    db: Session,
    session_id: UUID,
) -> Timeline:
    """
    Reconstruct a session timeline from persisted events.

    The Timeline is a read model generated from the
    Session and Event write models. Events are ordered
    chronologically using occurred_at.
    """

    # -----------------------------------------
    # Load Session
    # -----------------------------------------

    session = db.get(
        SessionModel,
        session_id,
    )

    if session is None:

        raise HTTPException(
            status_code=404,
            detail="Session not found."
        )

    # -----------------------------------------
    # Load Events
    # -----------------------------------------

    events = (
        db.query(Event)
        .filter(Event.session_id == session_id)
        .order_by(Event.occurred_at.asc())
        .all()
    )

    # -----------------------------------------
    # Convert Events
    # -----------------------------------------

    timeline_events = [

        TimelineEvent.model_validate(event)

        for event in events

    ]

    # -----------------------------------------
    # Build Timeline
    # -----------------------------------------

    return Timeline(

        session_id=session.id,

        started_at=session.started_at,

        ended_at=session.ended_at,

        events=timeline_events,

    )