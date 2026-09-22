from pathlib import Path

from observation.composition.composer import ProviderComposer
from observation.composition.factory import ProviderFactory
from observation.config.settings import ObservationSettings
from observation.core.enums import ProviderType
from observation.lifecycle.loader import ProviderLoader
from observation.providers.filesystem.provider import FilesystemProvider
from observation.providers.git.provider import GitProvider
from observation.providers.terminal.provider import TerminalProvider
from observation.registry.discovery import discover_providers
from observation.registry.registry import ProviderRegistry


def test_discovery_composition_registry_loader_flow(
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

    composed = composer.compose(discovered)

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

    loaded = loader.load()

    assert loaded == [
        composed[0],
        composed[2],
    ]