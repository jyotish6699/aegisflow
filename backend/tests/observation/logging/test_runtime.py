import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from observation.logging.runtime import ObservationRuntime
from observation.core.metadata import ObservationMetadata
from observation.core.observation import Observation
from observation.core.provider import ObservationProvider, ProviderType


pytestmark = pytest.mark.asyncio

def test_runtime_owns_resolved_workspace(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"

    runtime = ObservationRuntime(
        workspace,
        [],
        Mock(),
        Mock(),
    )

    assert runtime.workspace == workspace.resolve()


class FakeProvider(ObservationProvider):
    def __init__(self, provider_type: ProviderType, observe_fn) -> None:
        self._provider_type = provider_type
        self._observe_fn = observe_fn

    @property
    def provider_type(self) -> ProviderType:
        return self._provider_type

    async def initialize(self) -> None:
        pass

    async def start(self) -> None:
        pass

    async def observe(self):
        async for observation in self._observe_fn():
            yield observation

    async def stop(self) -> None:
        pass


def make_observation(
    provider: ProviderType,
    observation_type: str,
) -> Observation:
    return Observation(
        provider=provider,
        observation_type=observation_type,
        metadata=ObservationMetadata(
            source="test",
        ),
    )


async def test_runtime_observes_providers_concurrently(
    tmp_path: Path,
) -> None:
    terminal_ready = asyncio.Event()
    filesystem_release = asyncio.Event()

    terminal_observation = make_observation(
        ProviderType.TERMINAL,
        "command.completed",
    )

    filesystem_observation = make_observation(
        ProviderType.FILESYSTEM,
        "file.modified",
    )

    async def terminal_observe():
        terminal_ready.set()
        yield terminal_observation

        await filesystem_release.wait()

    async def filesystem_observe():
        await terminal_ready.wait()
        yield filesystem_observation

        filesystem_release.set()

    terminal = FakeProvider(
        ProviderType.TERMINAL,
        terminal_observe,
    )

    filesystem = FakeProvider(
        ProviderType.FILESYSTEM,
        filesystem_observe,
    )

    starter = Mock()
    starter.start_all = AsyncMock(
        return_value=[terminal, filesystem]
    )

    stopper = Mock()
    stopper.stop_all = AsyncMock(
        return_value=[]
    )

    runtime = ObservationRuntime(
        tmp_path,
        [terminal, filesystem],
        starter,
        stopper,
    )

    await runtime.start()

    stream = runtime.observe()

    first = await asyncio.wait_for(
        anext(stream),
        timeout=1,
    )

    second = await asyncio.wait_for(
        anext(stream),
        timeout=1,
    )

    assert {
        first.observation_type,
        second.observation_type,
    } == {
        "command.completed",
        "file.modified",
    }

    await runtime.stop()


async def test_runtime_isolates_provider_failure(
    tmp_path: Path,
) -> None:
    failure = RuntimeError("provider failed")

    failing_observation = make_observation(
        ProviderType.GIT,
        "branch.changed",
    )

    healthy_observation = make_observation(
        ProviderType.FILESYSTEM,
        "file.modified",
    )

    healthy_release = asyncio.Event()

    async def failing_observe():
        yield failing_observation
        raise failure

    async def healthy_observe():
        yield healthy_observation
        await healthy_release.wait()

    failing = FakeProvider(
        ProviderType.GIT,
        failing_observe,
    )

    healthy = FakeProvider(
        ProviderType.FILESYSTEM,
        healthy_observe,
    )

    starter = Mock()
    starter.start_all = AsyncMock(
        return_value=[failing, healthy]
    )

    stopper = Mock()
    stopper.stop_all = AsyncMock(
        return_value=[]
    )

    runtime = ObservationRuntime(
        tmp_path,
        [failing, healthy],
        starter,
        stopper,
    )

    await runtime.start()

    stream = runtime.observe()

    first = await asyncio.wait_for(
        anext(stream),
        timeout=1,
    )

    second = await asyncio.wait_for(
        anext(stream),
        timeout=1,
    )

    assert first.provider == ProviderType.GIT
    assert second.provider == ProviderType.FILESYSTEM

    healthy_release.set()

    await runtime.stop()


