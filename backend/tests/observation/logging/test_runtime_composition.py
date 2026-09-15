from pathlib import Path
from unittest.mock import AsyncMock

import pytest

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

    async def observe(self):
        if False:
            yield Observation(
                provider=self._provider_type,
                observation_type="test",
            )

    async def stop(self) -> None:
        pass


@pytest.mark.asyncio
async def test_runtime_accepts_composed_provider_instances(
    tmp_path: Path,
) -> None:
    providers = [
        FakeProvider(ProviderType.GIT),
        FakeProvider(ProviderType.FILESYSTEM),
    ]

    runtime = ObservationRuntime(
        workspace=tmp_path / "workspace",
        providers=providers,
    )

    assert runtime.workspace == (tmp_path / "workspace").resolve()
    assert runtime.providers == providers


@pytest.mark.asyncio
async def test_runtime_does_not_construct_providers(
    tmp_path: Path,
) -> None:
    providers = [
        FakeProvider(ProviderType.GIT),
    ]

    runtime = ObservationRuntime(
        workspace=tmp_path / "workspace",
        providers=providers,
    )

    assert runtime.providers is providers