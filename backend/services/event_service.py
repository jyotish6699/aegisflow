# Database session type
from sqlalchemy.orm import Session

# Event database model
from models.event import Event


# -------------------------------------------------
# Save Event
# -------------------------------------------------
# Receives event data from the API,
# creates an Event model,
# stores it in PostgreSQL,
# and returns the saved object.

def save_event(db: Session, event_data: dict):

    # Create Event model
    event = Event(
        session_id=event_data["session_id"],
        event_type=event_data["event_type"],
        occurred_at=event_data["occurred_at"],
        payload=event_data["payload"],
    )

    # Add object to current database session
    db.add(event)

    # Save changes permanently
    db.commit()

    # Reload object from database
    db.refresh(event)

    # Return saved event
    return event