from collections.abc import AsyncIterator

import pytest

from observation.core.enums import ProviderType
from observation.core.observation import Observation
from observation.core.provider import ObservationProvider
from observation.registry.registry import ProviderRegistry


class FakeProvider(ObservationProvider):
    """Minimal provider test double for registry tests."""

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


def test_register_and_get_provider() -> None:
    registry = ProviderRegistry()
    provider = FakeProvider(ProviderType.GIT)

    registry.register(provider)

    assert registry.get(ProviderType.GIT) is provider


def test_register_rejects_duplicate_provider_type() -> None:
    registry = ProviderRegistry()

    registry.register(
        FakeProvider(ProviderType.GIT)
    )

    with pytest.raises(
        ValueError,
        match="Provider already registered: git",
    ):
        registry.register(
            FakeProvider(ProviderType.GIT)
        )


def test_list_returns_registered_providers() -> None:
    registry = ProviderRegistry()

    git = FakeProvider(ProviderType.GIT)
    terminal = FakeProvider(ProviderType.TERMINAL)

    registry.register(git)
    registry.register(terminal)

    assert registry.list() == [git, terminal]


def test_unregister_removes_provider() -> None:
    registry = ProviderRegistry()
    provider = FakeProvider(ProviderType.GIT)

    registry.register(provider)
    registry.unregister(ProviderType.GIT)

    with pytest.raises(
        KeyError,
        match="Provider not registered: git",
    ):
        registry.get(ProviderType.GIT)