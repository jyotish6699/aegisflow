# UUID type
from uuid import UUID

# Date and time
from datetime import datetime

# Enum
from enum import Enum

# Pydantic base model
from pydantic import BaseModel


# -------------------------------------------------
# Session Status
# -------------------------------------------------

class SessionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"


# -------------------------------------------------
# Create Session Request
# -------------------------------------------------

class SessionCreate(BaseModel):
    project_name: str
    task_name: str
    notes: str | None = None


# -------------------------------------------------
# Update Session Request
# -------------------------------------------------

class SessionUpdate(BaseModel):
    project_name: str | None = None
    task_name: str | None = None
    notes: str | None = None
    status: SessionStatus | None = None
    ended_at: datetime | None = None


# -------------------------------------------------
# Session Response
# -------------------------------------------------

class SessionResponse(BaseModel):
    id: UUID
    project_name: str
    task_name: str
    notes: str | None
    status: SessionStatus
    started_at: datetime
    ended_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }