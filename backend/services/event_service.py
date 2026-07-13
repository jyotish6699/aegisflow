# Database session type
from sqlalchemy.orm import Session

# Event database model
from models.event import Event

# ---------------------------------
# Save Event
# ---------------------------------
# Receives event data from the API,
# creates an Event model,
# stores it in PostgreSQL,
# and returns the saved object.

def save_event(db: Session, event_data: dict):

    # Create Event Model

    print(event_data)

    event = Event(
        event_id=event_data["event_id"],
        type=event_data["type"],
        timestamp=event_data["timestamp"],
        payload=event_data["payload"]
    )

    # Add object to currect database session

    db.add(event)

    print("Added")

    # Save changes permanently

    db.commit()

    print("Committed")

    # Reload object from database
    
    db.refresh(event)

    print("Refreshed")

    # Return saved event

    return event