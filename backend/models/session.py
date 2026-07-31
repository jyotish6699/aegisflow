# UUID generation
import uuid

# Date and time
from datetime import datetime
from enum import Enum

# SQLAlchemy column types
from sqlalchemy import String, Text, DateTime, Enum as SQLAlchemyEnum

# PostgreSQL UUID type
from sqlalchemy.dialects.postgresql import UUID

# SQLAlchemy ORM mapping
from sqlalchemy.orm import Mapped, mapped_column

# Base model
from database import Base


# -------------------------------------------------
# Session Status
# -------------------------------------------------

class SessionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"


# -------------------------------------------------
# Session Model
# -------------------------------------------------

class Session(Base):

    __tablename__ = "sessions"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Workspace Information
    project_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    task_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Session Status
    status: Mapped[SessionStatus] = mapped_column(
        SQLAlchemyEnum(SessionStatus),
        nullable=False,
        default=SessionStatus.ACTIVE,
    )

    # Session Lifecycle
    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    # Audit Fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )