# Pydantic base class
from pydantic import BaseModel

# UUID type
from uuid import UUID

# Python datetime
from datetime import datetime

# ------------------------
# Event Request Schema
# ------------------------
# Defines the structure of an incoming event request from the frontend

class EventCreate(BaseModel):

    event_id: UUID

    type: str

    timestamp: datetime

    payload: dict