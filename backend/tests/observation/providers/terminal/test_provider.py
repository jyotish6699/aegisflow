from pathlib import Path

import pytest

from observation.core.enums import ProviderType
from observation.providers.terminal.provider import TerminalProvider


@pytest.mark.asyncio
async def test_terminal_provider_has_correct_provider_type(
    tmp_path: Path,
) -> None:
    """
    TerminalProvider should identify itself as the Terminal provider.
    """

    protocol = tmp_path / "protocol.jsonl"

    provider = TerminalProvider(protocol)

    assert provider.provider_type == ProviderType.TERMINAL


@pytest.mark.asyncio
async def test_terminal_provider_does_not_observe_before_start(
    tmp_path: Path,
) -> None:
    """
    TerminalProvider should not produce observations before start().
    """

    protocol = tmp_path / "protocol.jsonl"

    provider = TerminalProvider(protocol)

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

    provider = TerminalProvider(protocol)

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

    provider = TerminalProvider(protocol)

    await provider.initialize()
    await provider.start()
    await provider.stop()

    observations = [
        observation
        async for observation in provider.observe()
    ]

    assert observations == []