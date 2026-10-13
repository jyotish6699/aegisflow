"""Versioned events emitted by the terminal capture helper."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Literal

OutputStream = Literal["stdout", "stderr"]


@dataclass(frozen=True)
class CaptureEvent:
    session_id: str
    command_id: str
    sequence: int
    event_type: str
    timestamp: str
    fields: dict[str, Any]
    version: int = 1

    @classmethod
    def create(
        cls,
        *,
        session_id: str,
        command_id: str,
        sequence: int,
        event_type: str,
        **fields: Any,
    ) -> "CaptureEvent":
        return cls(
            session_id=session_id,
            command_id=command_id,
            sequence=sequence,
            event_type=event_type,
            timestamp=datetime.now(timezone.utc).isoformat(),
            fields=fields,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "session_id": self.session_id,
            "command_id": self.command_id,
            "sequence": self.sequence,
            "timestamp": self.timestamp,
            "type": self.event_type,
            **self.fields,
        }
