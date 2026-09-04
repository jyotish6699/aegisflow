from pathlib import Path
from enum import StrEnum

from pydantic import BaseModel


# =====================================================
# Filesystem Event Types
# =====================================================

class FilesystemEventType(StrEnum):
    """
    Internal filesystem event types.

    These represent normalized filesystem activity
    before it becomes a canonical Observation.
    """

    CREATED = "created"

    MODIFIED = "modified"

    DELETED = "deleted"


# =====================================================
# Filesystem Event
# =====================================================

class FilesystemEvent(BaseModel):
    """
    Internal normalized filesystem event.

    This model sits between the low-level filesystem
    watcher and the Filesystem Provider.

    It contains only filesystem facts required by the
    provider and carries no business interpretation.
    """

    event_type: FilesystemEventType

    path: Path