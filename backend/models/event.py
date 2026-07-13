# PostgreSQL column data types
from sqlalchemy import String, DateTime

# PostgreSQL JSON data type 
from sqlalchemy.dialects.postgresql import JSONB

# UUID support 
from sqlalchemy.dialects.postgresql import UUID

# Maps Python attributes to database columns
from sqlalchemy.orm import Mapped, mapped_column

# Base class for every database model 
from database import Base

# -------------------------------------------------
# Event Model
# -------------------------------------------------
# This class represents the "events" table inside postgreSQL.

# Every attributes below becomes one column inside the table.

class Event(Base):

    # Name of the table inside PostgreSQL
    __tablename__ = "events"

    # ---------------------------
    # Primary Key
    # ---------------------------
    # Every event has a globally unique identifier.

    event_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True
    )

    # ----------------------------
    # Event Type
    # ----------------------------
    
    type: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    # --------------------------
    # Event timestamp
    # --------------------------
    # Time when the event occurred.

    timestamp: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=False
    )

    # --------------------------
    # Event Payload
    # --------------------------
    # Stores event-specific information
    # Ex.: "project": "Aegisflow"

    payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False
    )