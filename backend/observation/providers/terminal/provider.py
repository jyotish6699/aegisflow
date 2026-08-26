import json
from collections.abc import AsyncIterator
from pathlib import Path

from observation.core.enums import ProviderType
from observation.core.metadata import ObservationMetadata
from observation.core.observation import Observation
from observation.core.provider import ObservationProvider


class TerminalProvider(ObservationProvider):
    """
    Observation Provider for terminal command lifecycle activity.

    The Terminal Provider consumes command lifecycle messages
    produced by the terminal integration layer and converts
    them into canonical AegisFlow Observation objects.
    """

    def __init__(self, workspace: Path, protocol: Path) -> None:
        self._workspace = workspace.resolve()
        self._protocol = protocol.resolve()

        self._started = False
        self._offset = 0

    @property
    def provider_type(self) -> ProviderType:
        """Return the Terminal provider identity."""
        return ProviderType.TERMINAL

    async def initialize(self) -> None:
        """
        Prepare the Terminal Provider.

        Observation does not begin during initialization.
        """
        self._offset = 0

    async def start(self) -> None:
        """
        Activate the Terminal Provider.
        """
        self._started = True

    async def observe(self) -> AsyncIterator[Observation]:
        """
        Consume newly written terminal protocol messages and
        convert them into canonical Observation objects.
        """
        if not self._started:
            return

        if not self._protocol.exists():
            return

        lines = self._protocol.read_text().splitlines()

        new_lines = lines[self._offset :]
        self._offset = len(lines)

        for line in new_lines:
            if not line.strip():
                continue

            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                continue

            observation_type = message.get("type")

            if observation_type not in {
                "command.started",
                "command.completed",
            }:
                continue

            yield Observation(
                provider=ProviderType.TERMINAL,
                observation_type=observation_type,
                metadata=ObservationMetadata(
                    source="terminal",
                    attributes={
                        "workspace": str(self._workspace),
                        "command_id": message["command_id"],
                        "command": message["command"],
                        "cwd": message["cwd"],
                        **{
                            key: value
                            for key, value in message.items()
                            if key
                            not in {
                                "type",
                                "command_id",
                                "command",
                                "cwd",
                            }
                        },
                    },
                ),
            )

    async def stop(self) -> None:
        """
        Stop the Terminal Provider and release provider state.
        """
        self._started = False
        self._offset = 0