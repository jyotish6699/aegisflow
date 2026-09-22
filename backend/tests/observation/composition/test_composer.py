import pytest
from pathlib import Path

from observation.composition.composer import ProviderComposer
from observation.composition.factory import ProviderFactory
from observation.core.enums import ProviderType
from observation.providers.filesystem.provider import FilesystemProvider
from observation.providers.git.provider import GitProvider
from observation.providers.terminal.provider import TerminalProvider
from observation.registry.registry import ProviderRegistry


def create_composer(
    tmp_path: Path,
) -> tuple[ProviderComposer, ProviderRegistry]:
    factory = ProviderFactory(
        workspace=tmp_path / "workspace",
        terminal_protocol=tmp_path / "terminal.jsonl",
    )

    registry = ProviderRegistry()

    composer = ProviderComposer(
        factory=factory,
        registry=registry,
    )

    return composer, registry


def test_composer_constructs_and_registers_providers(
    tmp_path: Path,
) -> None:
    composer, registry = create_composer(tmp_path)

    providers = composer.compose(
        [
            GitProvider,
            TerminalProvider,
            FilesystemProvider,
        ]
    )

    assert [provider.provider_type for provider in providers] == [
        ProviderType.GIT,
        ProviderType.TERMINAL,
        ProviderType.FILESYSTEM,
    ]

    assert registry.list() == providers


def test_composer_registers_each_created_provider(
    tmp_path: Path,
) -> None:
    composer, registry = create_composer(tmp_path)

    providers = composer.compose(
        [
            GitProvider,
            TerminalProvider,
        ]
    )

    assert registry.get(ProviderType.GIT) is providers[0]
    assert registry.get(ProviderType.TERMINAL) is providers[1]


def test_composer_returns_created_provider_instances(
    tmp_path: Path,
) -> None:
    composer, _ = create_composer(tmp_path)

    providers = composer.compose([GitProvider])

    assert len(providers) == 1
    assert isinstance(providers[0], GitProvider)


def test_composer_preserves_provider_order(
    tmp_path: Path,
) -> None:
    composer, registry = create_composer(tmp_path)

    providers = composer.compose(
        [
            FilesystemProvider,
            GitProvider,
        ]
    )

    assert [provider.provider_type for provider in providers] == [
        ProviderType.FILESYSTEM,
        ProviderType.GIT,
    ]

    assert registry.list() == providers


def test_composer_does_not_partially_register_on_factory_failure(
    tmp_path: Path,
) -> None:
    class FailingFactory:
        def create(self, providers):
            raise RuntimeError("provider construction failed")

    registry = ProviderRegistry()

    composer = ProviderComposer(
        factory=FailingFactory(),
        registry=registry,
    )

    with pytest.raises(
        RuntimeError,
        match="provider construction failed",
    ):
        composer.compose([GitProvider])

    assert registry.list() == []