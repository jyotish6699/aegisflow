from collections.abc import AsyncIterator

import pytest

from observation.core.enums import ProviderType
from observation.core.observation import Observation
from observation.core.provider import ObservationProvider
from observation.lifecycle.health import (
    ProviderHealth,
    ProviderHealthTracker,
)
from observation.lifecycle.stopper import ProviderStopper


class FakeProvider(ObservationProvider):
    """Provider test double for stopper tests."""

    def __init__(
        self,
        provider_type: ProviderType,
        fail_stop: bool = False,
    ) -> None:
        self._provider_type = provider_type
        self._fail_stop = fail_stop

        self.stopped = False

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
        if self._fail_stop:
            raise RuntimeError("shutdown failed")

        self.stopped = True


@pytest.mark.asyncio
async def test_stop_stops_provider() -> None:
    health = ProviderHealthTracker()
    stopper = ProviderStopper(health)
    provider = FakeProvider(ProviderType.GIT)

    result = await stopper.stop(provider)

    assert result is True
    assert provider.stopped is True
    assert health.get_state(ProviderType.GIT) == ProviderHealth.STOPPED


@pytest.mark.asyncio
async def test_stop_updates_stopping_before_stopped() -> None:
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
    stopper = ProviderStopper(health)
    provider = FakeProvider(ProviderType.GIT)

    result = await stopper.stop(provider)

    assert result is True
    assert states == [
        ProviderHealth.STOPPING,
        ProviderHealth.STOPPED,
    ]


@pytest.mark.asyncio
async def test_stop_handles_failure() -> None:
    health = ProviderHealthTracker()
    stopper = ProviderStopper(health)

    provider = FakeProvider(
        ProviderType.GIT,
        fail_stop=True,
    )

    result = await stopper.stop(provider)

    assert result is False
    assert provider.stopped is False
    assert health.get_state(ProviderType.GIT) == ProviderHealth.FAILED


@pytest.mark.asyncio
async def test_stop_all_isolates_provider_failure() -> None:
    health = ProviderHealthTracker()
    stopper = ProviderStopper(health)

    failing = FakeProvider(
        ProviderType.GIT,
        fail_stop=True,
    )
    healthy = FakeProvider(
        ProviderType.TERMINAL,
    )

    stopped = await stopper.stop_all(
        [failing, healthy]
    )

    assert stopped == [healthy]

    assert health.get_state(ProviderType.GIT) == ProviderHealth.FAILED
    assert health.get_state(ProviderType.TERMINAL) == ProviderHealth.STOPPED

    assert healthy.stopped is True


@pytest.mark.asyncio
async def test_stop_all_preserves_input_order() -> None:
    health = ProviderHealthTracker()
    stopper = ProviderStopper(health)

    git = FakeProvider(ProviderType.GIT)
    terminal = FakeProvider(ProviderType.TERMINAL)

    stopped = await stopper.stop_all(
        [git, terminal]
    )

    assert stopped == [git, terminal]