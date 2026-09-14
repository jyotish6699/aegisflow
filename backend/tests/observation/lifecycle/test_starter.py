from collections.abc import AsyncIterator

import pytest

from observation.core.enums import ProviderType
from observation.core.observation import Observation
from observation.core.provider import ObservationProvider
from observation.lifecycle.health import (
    ProviderHealth,
    ProviderHealthTracker,
)
from observation.lifecycle.starter import ProviderStarter


class FakeProvider(ObservationProvider):
    """Provider test double for starter tests."""

    def __init__(
        self,
        provider_type: ProviderType,
        fail_initialize: bool = False,
        fail_start: bool = False,
    ) -> None:
        self._provider_type = provider_type
        self._fail_initialize = fail_initialize
        self._fail_start = fail_start

        self.initialized = False
        self.started = False

    @property
    def provider_type(self) -> ProviderType:
        return self._provider_type

    async def initialize(self) -> None:
        if self._fail_initialize:
            raise RuntimeError("initialization failed")

        self.initialized = True

    async def start(self) -> None:
        if self._fail_start:
            raise RuntimeError("startup failed")

        self.started = True

    async def observe(self) -> AsyncIterator[Observation]:
        if False:
            yield

    async def stop(self) -> None:
        self.started = False


@pytest.mark.asyncio
async def test_start_initializes_and_starts_provider() -> None:
    health = ProviderHealthTracker()
    starter = ProviderStarter(health)
    provider = FakeProvider(ProviderType.GIT)

    result = await starter.start(provider)

    assert result is True
    assert provider.initialized is True
    assert provider.started is True
    assert health.get_state(ProviderType.GIT) == ProviderHealth.RUNNING


@pytest.mark.asyncio
async def test_start_updates_ready_before_running() -> None:
    states: list[ProviderHealth] = []

    class TrackingHealth(ProviderHealthTracker):
        def set_state(
            self,
            provider_type: ProviderType,
            state: ProviderHealth,
        ) -> None:
            states.append(state)
            super().set_state(provider_type, state)

    health = TrackingHealth()
    starter = ProviderStarter(health)
    provider = FakeProvider(ProviderType.GIT)

    result = await starter.start(provider)

    assert result is True
    assert states == [
        ProviderHealth.INITIALIZING,
        ProviderHealth.READY,
        ProviderHealth.RUNNING,
    ]


@pytest.mark.asyncio
async def test_start_handles_initialization_failure() -> None:
    health = ProviderHealthTracker()
    starter = ProviderStarter(health)

    provider = FakeProvider(
        ProviderType.GIT,
        fail_initialize=True,
    )

    result = await starter.start(provider)

    assert result is False
    assert provider.initialized is False
    assert provider.started is False
    assert health.get_state(ProviderType.GIT) == ProviderHealth.FAILED


@pytest.mark.asyncio
async def test_start_handles_start_failure() -> None:
    health = ProviderHealthTracker()
    starter = ProviderStarter(health)

    provider = FakeProvider(
        ProviderType.GIT,
        fail_start=True,
    )

    result = await starter.start(provider)

    assert result is False
    assert provider.initialized is True
    assert provider.started is False
    assert health.get_state(ProviderType.GIT) == ProviderHealth.FAILED


@pytest.mark.asyncio
async def test_start_all_isolates_provider_failure() -> None:
    health = ProviderHealthTracker()
    starter = ProviderStarter(health)

    failing = FakeProvider(
        ProviderType.GIT,
        fail_start=True,
    )
    healthy = FakeProvider(
        ProviderType.TERMINAL,
    )

    started = await starter.start_all(
        [failing, healthy]
    )

    assert started == [healthy]

    assert health.get_state(ProviderType.GIT) == ProviderHealth.FAILED
    assert health.get_state(ProviderType.TERMINAL) == ProviderHealth.RUNNING

    assert healthy.started is True


@pytest.mark.asyncio
async def test_start_all_preserves_input_order() -> None:
    health = ProviderHealthTracker()
    starter = ProviderStarter(health)

    git = FakeProvider(ProviderType.GIT)
    terminal = FakeProvider(ProviderType.TERMINAL)

    started = await starter.start_all(
        [git, terminal]
    )

    assert started == [git, terminal]