import pytest
from collections.abc import AsyncIterator
from pathlib import Path

from observation.core.enums import ProviderType
from observation.core.observation import Observation
from observation.core.provider import ObservationProvider
from observation.logging.runtime import ObservationRuntime


class FakeProvider(ObservationProvider):
    def __init__(self, provider_type: ProviderType) -> None:
        self._provider_type = provider_type

    @property
    def provider_type(self) -> ProviderType:
        return self._provider_type

    async def initialize(self) -> None:
        pass

    async def start(self) -> None:
        pass

    async def observe(self) -> AsyncIterator[Observation]:
        if False:
            yield

    async def stop(self) -> None:
        pass


class FakeStarter:
    def __init__(self) -> None:
        self.started = None

    async def start_all(self, providers):
        self.started = providers
        return providers


class FakeStopper:
    async def stop_all(self, providers):
        return providers


def test_runtime_accepts_external_provider_lifecycle_dependencies(
    tmp_path: Path,
) -> None:
    providers = [
        FakeProvider(ProviderType.GIT),
        FakeProvider(ProviderType.FILESYSTEM),
    ]

    starter = FakeStarter()
    stopper = FakeStopper()

    runtime = ObservationRuntime(
        workspace=tmp_path / "workspace",
        providers=providers,
        starter=starter,
        stopper=stopper,
    )

    assert runtime.workspace == (
        tmp_path / "workspace"
    ).resolve()


@pytest.mark.asyncio
async def test_runtime_start_delegates_to_starter(
    tmp_path: Path,
) -> None:
    providers = [
        FakeProvider(ProviderType.GIT),
        FakeProvider(ProviderType.FILESYSTEM),
    ]

    starter = FakeStarter()
    stopper = FakeStopper()

    runtime = ObservationRuntime(
        workspace=tmp_path / "workspace",
        providers=providers,
        starter=starter,
        stopper=stopper,
    )

    await runtime.start()

    assert starter.started == providers