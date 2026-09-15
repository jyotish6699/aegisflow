from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from observation.composition.composer import ProviderComposer
from observation.composition.factory import ProviderFactory
from observation.config.settings import ObservationSettings
from observation.core.enums import ProviderType
from observation.lifecycle.health import (
    ProviderHealth,
    ProviderHealthTracker,
)
from observation.lifecycle.loader import ProviderLoader
from observation.lifecycle.starter import ProviderStarter
from observation.lifecycle.stopper import ProviderStopper
from observation.providers.filesystem.provider import FilesystemProvider
from observation.providers.git.provider import GitProvider
from observation.providers.terminal.provider import TerminalProvider
from observation.registry.discovery import discover_providers
from observation.registry.registry import ProviderRegistry


@pytest.mark.asyncio
async def test_composed_providers_follow_start_and_stop_flow(
    tmp_path: Path,
) -> None:
    discovered = discover_providers(
        [
            GitProvider,
            TerminalProvider,
            FilesystemProvider,
        ]
    )

    factory = ProviderFactory(
        workspace=tmp_path / "workspace",
        terminal_protocol=tmp_path / "terminal.jsonl",
    )

    registry = ProviderRegistry()

    composer = ProviderComposer(
        factory=factory,
        registry=registry,
    )

    composer.compose(discovered)

    settings = ObservationSettings(
        enabled=True,
        providers=[
            ProviderType.GIT,
            ProviderType.FILESYSTEM,
        ],
    )

    loader = ProviderLoader(
        registry=registry,
        settings=settings,
    )

    selected = loader.load()

    for provider in selected:
        provider.initialize = AsyncMock()
        provider.start = AsyncMock()
        provider.stop = AsyncMock()

    health = ProviderHealthTracker()

    starter = ProviderStarter(health)
    stopper = ProviderStopper(health)

    started = await starter.start_all(selected)

    assert started == selected

    assert health.get_state(ProviderType.GIT) == ProviderHealth.RUNNING
    assert (
        health.get_state(ProviderType.FILESYSTEM)
        == ProviderHealth.RUNNING
    )

    stopped = await stopper.stop_all(started)

    assert stopped == started

    assert health.get_state(ProviderType.GIT) == ProviderHealth.STOPPED
    assert (
        health.get_state(ProviderType.FILESYSTEM)
        == ProviderHealth.STOPPED
    )