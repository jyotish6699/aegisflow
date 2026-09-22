from collections.abc import AsyncIterator

from observation.config.settings import ObservationSettings
from observation.core.enums import ProviderType
from observation.core.observation import Observation
from observation.core.provider import ObservationProvider
from observation.lifecycle.loader import ProviderLoader
from observation.registry.registry import ProviderRegistry


class FakeProvider(ObservationProvider):
    """Minimal provider test double for loader tests."""

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


def test_loader_returns_enabled_registered_providers() -> None:
    registry = ProviderRegistry()

    git = FakeProvider(ProviderType.GIT)
    terminal = FakeProvider(ProviderType.TERMINAL)

    registry.register(git)
    registry.register(terminal)

    settings = ObservationSettings(
        enabled=True,
        providers=[
            ProviderType.GIT,
            ProviderType.TERMINAL,
        ],
    )

    loader = ProviderLoader(registry, settings)

    assert loader.load() == [git, terminal]


def test_loader_returns_only_configured_providers() -> None:
    registry = ProviderRegistry()

    git = FakeProvider(ProviderType.GIT)
    terminal = FakeProvider(ProviderType.TERMINAL)

    registry.register(git)
    registry.register(terminal)

    settings = ObservationSettings(
        enabled=True,
        providers=[ProviderType.GIT],
    )

    loader = ProviderLoader(registry, settings)

    assert loader.load() == [git]


def test_loader_preserves_configuration_order() -> None:
    registry = ProviderRegistry()

    git = FakeProvider(ProviderType.GIT)
    terminal = FakeProvider(ProviderType.TERMINAL)

    registry.register(git)
    registry.register(terminal)

    settings = ObservationSettings(
        enabled=True,
        providers=[
            ProviderType.TERMINAL,
            ProviderType.GIT,
        ],
    )

    loader = ProviderLoader(registry, settings)

    assert loader.load() == [terminal, git]


def test_loader_returns_empty_when_observation_is_disabled() -> None:
    registry = ProviderRegistry()

    registry.register(
        FakeProvider(ProviderType.GIT)
    )

    settings = ObservationSettings(
        enabled=False,
        providers=[ProviderType.GIT],
    )

    loader = ProviderLoader(registry, settings)

    assert loader.load() == []