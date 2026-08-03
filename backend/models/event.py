# UUID generation
import uuid

# Date and time
from datetime import datetime

# SQLAlchemy column types
from sqlalchemy import String, DateTime, ForeignKey

# PostgreSQL column types
from sqlalchemy.dialects.postgresql import UUID, JSONB

# SQLAlchemy ORM
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Base model
from database import Base


# -------------------------------------------------
# Event Model
# -------------------------------------------------

class Event(Base):

    __tablename__ = "events"

    # -------------------------------------------------
    # Primary Key
    # -------------------------------------------------

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # -------------------------------------------------
    # Parent Session
    # -------------------------------------------------

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id"),
        nullable=False,
    )

    # -------------------------------------------------
    # Event Type
    # -------------------------------------------------

    event_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    # -------------------------------------------------
    # Business Timestamp
    # -------------------------------------------------

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    # -------------------------------------------------
    # Event Data
    # -------------------------------------------------

    payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    # -------------------------------------------------
    # Audit Timestamp
    # -------------------------------------------------

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    # -------------------------------------------------
    # Relationship
    # -------------------------------------------------

    session = relationship(
        "Session",
        back_populates="events",
    )