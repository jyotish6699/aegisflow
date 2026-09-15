from pathlib import Path

from observation.composition.composer import ProviderComposer
from observation.composition.factory import ProviderFactory
from observation.core.enums import ProviderType
from observation.registry.discovery import discover_providers
from observation.registry.registry import ProviderRegistry
from observation.providers.filesystem.provider import FilesystemProvider
from observation.providers.git.provider import GitProvider
from observation.providers.terminal.provider import TerminalProvider


def test_discovery_factory_registry_flow(
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

    providers = composer.compose(discovered)

    assert [provider.provider_type for provider in providers] == [
        ProviderType.GIT,
        ProviderType.TERMINAL,
        ProviderType.FILESYSTEM,
    ]

    assert registry.list() == providers