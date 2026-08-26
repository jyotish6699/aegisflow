from pathlib import Path
import json

import pytest

from observation.core.enums import ProviderType
from observation.core.observation import Observation
from observation.providers.terminal.provider import TerminalProvider


@pytest.mark.asyncio
async def test_terminal_provider_has_correct_provider_type(
    tmp_path: Path,
) -> None:
    """
    TerminalProvider should identify itself as the Terminal provider.
    """

    protocol = tmp_path / "protocol.jsonl"

    provider = TerminalProvider(tmp_path, protocol)

    assert provider.provider_type == ProviderType.TERMINAL


@pytest.mark.asyncio
async def test_terminal_provider_does_not_observe_before_start(
    tmp_path: Path,
) -> None:
    """
    TerminalProvider should not produce observations before start().
    """

    protocol = tmp_path / "protocol.jsonl"

    provider = TerminalProvider(tmp_path, protocol)

    await provider.initialize()

    observations = [
        observation
        async for observation in provider.observe()
    ]

    assert observations == []


@pytest.mark.asyncio
async def test_terminal_provider_does_not_observe_when_protocol_is_missing(
    tmp_path: Path,
) -> None:
    """
    TerminalProvider should produce no observations when the
    terminal protocol does not exist.
    """

    protocol = tmp_path / "protocol.jsonl"

    provider = TerminalProvider(tmp_path, protocol)

    await provider.initialize()
    await provider.start()

    observations = [
        observation
        async for observation in provider.observe()
    ]

    assert observations == []


@pytest.mark.asyncio
async def test_terminal_provider_stops_observation(
    tmp_path: Path,
) -> None:
    """
    TerminalProvider should stop producing observations after stop().
    """

    protocol = tmp_path / "protocol.jsonl"

    provider = TerminalProvider(tmp_path, protocol)

    await provider.initialize()
    await provider.start()
    await provider.stop()

    observations = [
        observation
        async for observation in provider.observe()
    ]

    assert observations == []


@pytest.mark.asyncio
async def test_terminal_provider_emits_command_started_observation(
    tmp_path: Path,
) -> None:
    protocol = tmp_path / "aegisflow-protocol.jsonl"

    protocol.write_text(
        json.dumps(
            {
                "type": "command.started",
                "command_id": "123-456",
                "command": "printf 'hello'",
                "cwd": str(tmp_path),
            }
        )
        + "\n"
    )

    provider = TerminalProvider(tmp_path, protocol)

    await provider.initialize()
    await provider.start()

    observations = [
        observation
        async for observation in provider.observe()
    ]

    assert len(observations) == 1

    observation = observations[0]

    assert observation.provider == ProviderType.TERMINAL
    assert observation.observation_type == "command.started"

    assert observation.metadata.source == "terminal"

    assert observation.metadata.attributes == {
        "workspace": str(tmp_path),
        "command_id": "123-456",
        "command": "printf 'hello'",
        "cwd": str(tmp_path),
    }


@pytest.mark.asyncio
async def test_terminal_provider_emits_command_completed_observation(
    tmp_path: Path,
) -> None:
    protocol = tmp_path / "aegisflow-protocol.jsonl"

    protocol.write_text(
        json.dumps(
            {
                "type": "command.completed",
                "command_id": "123-456",
                "command": "printf 'hello'",
                "cwd": str(tmp_path),
                "exit_code": 0,
                "duration": 0.125,
            }
        )
        + "\n"
    )

    provider = TerminalProvider(tmp_path, protocol)

    await provider.initialize()
    await provider.start()

    observations = [
        observation
        async for observation in provider.observe()
    ]

    assert len(observations) == 1

    observation = observations[0]

    assert observation.provider == ProviderType.TERMINAL
    assert observation.observation_type == "command.completed"

    assert observation.metadata.source == "terminal"

    assert observation.metadata.attributes == {
        "workspace": str(tmp_path),
        "command_id": "123-456",
        "command": "printf 'hello'",
        "cwd": str(tmp_path),
        "exit_code": 0,
        "duration": 0.125,
    }