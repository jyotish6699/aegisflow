import asyncio
import json
from collections.abc import AsyncIterator
from datetime import datetime
from pathlib import Path
from typing import Any

from observation.core.enums import ProviderType
from observation.core.metadata import ObservationMetadata
from observation.core.observation import Observation
from observation.core.provider import ObservationProvider
from observation.providers.terminal.capture.transport import (
    SessionTransportServer,
)


class TerminalProvider(ObservationProvider):
    """
    Observation Provider for terminal command lifecycle activity.

    The Terminal Provider consumes command lifecycle messages
    produced by the terminal integration layer and converts
    them into canonical AegisFlow Observation objects.
    """

    def __init__(
        self,
        workspace: Path,
        protocol: Path,
        capture_endpoint: Path | None = None,
    ) -> None:
        self._workspace = workspace.resolve()
        self._protocol = protocol.resolve()
        self._capture_endpoint = (
            capture_endpoint.resolve()
            if capture_endpoint is not None
            else None
        )

        self._started = False
        self._offset = 0
        self._capture_server: SessionTransportServer | None = None

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
        if self._capture_endpoint is not None:
            self._capture_server = SessionTransportServer(
                self._capture_endpoint
            )

    async def start(self) -> None:
        """
        Activate the Terminal Provider.
        """
        self._started = True

    async def observe(self) -> AsyncIterator[Observation]:
        """
        Continuously consume lifecycle and capture protocol messages.
        """
        capture_reader: asyncio.StreamReader | None = None
        capture_writer: asyncio.StreamWriter | None = None
        capture_accept_task: asyncio.Task[object] | None = None
        command_completed = False

        try:
            while self._started:
                if (
                    self._capture_server is not None
                    and capture_reader is None
                ):
                    if capture_accept_task is None:
                        capture_accept_task = asyncio.create_task(
                            self._capture_server.accept_async()
                        )
                    if capture_accept_task.done():
                        connection = capture_accept_task.result()
                        capture_accept_task = None
                        if connection is None:
                            continue
                        capture_reader, capture_writer = (
                            await asyncio.open_connection(sock=connection)
                        )
                        command_completed = False

                if capture_reader is not None:
                    try:
                        line = await asyncio.wait_for(
                            capture_reader.readline(),
                            timeout=0.05,
                        )
                    except asyncio.TimeoutError:
                        line = None

                    if line == b"":
                        if not command_completed:
                            raise RuntimeError(
                                "terminal capture transport disconnected"
                            )
                        capture_reader = None
                        capture_writer.close()
                        await capture_writer.wait_closed()
                        capture_writer = None
                        continue
                    if line:
                        observation = self._capture_observation(line)
                        if observation is not None:
                            if (
                                observation.observation_type
                                == "command.completed"
                            ):
                                command_completed = True
                            yield observation
                        continue

                for observation in self._legacy_observations():
                    yield observation

                await asyncio.sleep(0.05)
        finally:
            if capture_accept_task is not None:
                capture_accept_task.cancel()
                await asyncio.gather(
                    capture_accept_task,
                    return_exceptions=True,
                )
            if capture_writer is not None:
                capture_writer.close()
                await capture_writer.wait_closed()
            if self._capture_server is not None:
                self._capture_server.close()
                self._capture_server = None

    def _legacy_observations(self) -> list[Observation]:
        if not self._protocol.exists():
            return []

        try:
            lines = self._protocol.read_text().splitlines()
        except OSError:
            return []

        if self._offset > len(lines):
            self._offset = 0

        new_lines = lines[self._offset:]
        self._offset = len(lines)

        observations: list[Observation] = []
        for line in new_lines:
            if not line.strip():
                continue

            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                continue

            observation = self._observation_from_message(
                message,
                allowed_types={"command.started", "command.completed"},
            )
            if observation is not None:
                observations.append(observation)
        return observations

    def _capture_observation(
        self,
        line: bytes,
    ) -> Observation | None:
        try:
            message = json.loads(line)
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None
        return self._observation_from_message(
            message,
            allowed_types={
                "command.started",
                "terminal.output",
                "command.completed",
            },
        )

    def _observation_from_message(
        self,
        message: Any,
        *,
        allowed_types: set[str],
    ) -> Observation | None:
        if not isinstance(message, dict):
            return None

        observation_type = message.get("type")
        if observation_type not in allowed_types:
            return None

        cwd_value = message.get("cwd")
        command_id = message.get("command_id")
        if not isinstance(cwd_value, str) or not isinstance(
            command_id,
            str,
        ):
            return None

        cwd = Path(cwd_value).resolve()
        try:
            cwd.relative_to(self._workspace)
        except ValueError:
            return None

        required_capture_fields = {
            "session_id",
            "sequence",
            "timestamp",
        }
        if (
            observation_type == "terminal.output"
            and not required_capture_fields <= message.keys()
        ):
            return None

        attributes = {
            "workspace": str(self._workspace),
            "command_id": command_id,
            "cwd": str(cwd),
            **{
                key: value
                for key, value in message.items()
                if key not in {"type", "cwd"}
            },
        }

        occurred_at = None
        timestamp = message.get("timestamp")
        if isinstance(timestamp, str):
            try:
                occurred_at = datetime.fromisoformat(timestamp)
            except ValueError:
                pass

        observation_data: dict[str, Any] = {
            "provider": ProviderType.TERMINAL,
            "observation_type": observation_type,
            "metadata": ObservationMetadata(
                source="terminal",
                attributes=attributes,
            ),
        }
        if occurred_at is not None:
            observation_data["occurred_at"] = occurred_at
        return Observation(**observation_data)

    async def stop(self) -> None:
        """
        Stop the Terminal Provider and release provider state.
        """
        self._started = False
        self._offset = 0
        if self._capture_server is not None:
            self._capture_server.close()
            self._capture_server = None