from collections.abc import AsyncIterator

from observation.core.enums import ProviderType
from observation.core.observation import Observation
from observation.core.provider import ObservationProvider
from observation.registry.discovery import discover_providers


class FakeProvider(ObservationProvider):
    """Minimal provider class for discovery tests."""

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.GIT

    async def initialize(self) -> None:
        pass

    async def start(self) -> None:
        pass

    async def observe(self) -> AsyncIterator[Observation]:
        if False:
            yield

    async def stop(self) -> None:
        pass


def test_discover_providers_returns_provider_classes() -> None:
    result = discover_providers([FakeProvider])

    assert result == [FakeProvider]


def test_discover_providers_returns_new_list() -> None:
    providers = [FakeProvider]

    result = discover_providers(providers)

    assert result is not providers
    assert result == providers


def test_discover_providers_preserves_provider_order() -> None:
    class SecondProvider(FakeProvider):
        @property
        def provider_type(self) -> ProviderType:
            return ProviderType.TERMINAL

    providers = [FakeProvider, SecondProvider]

    result = discover_providers(providers)

    assert result == [FakeProvider, SecondProvider]


def test_discover_providers_accepts_empty_input() -> None:
    assert discover_providers([]) == []