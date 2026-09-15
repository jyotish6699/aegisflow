from pathlib import Path

import pytest

from observation.composition.factory import ProviderFactory
from observation.core.enums import ProviderType
from observation.providers.filesystem.provider import FilesystemProvider
from observation.providers.git.provider import GitProvider
from observation.providers.terminal.provider import TerminalProvider


def create_factory(tmp_path: Path) -> ProviderFactory:
    return ProviderFactory(
        workspace=tmp_path / "workspace",
        terminal_protocol=tmp_path / "terminal.jsonl",
    )


def test_factory_constructs_requested_providers(
    tmp_path: Path,
) -> None:
    factory = create_factory(tmp_path)

    providers = factory.create(
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


def test_factory_preserves_requested_order(
    tmp_path: Path,
) -> None:
    factory = create_factory(tmp_path)

    providers = factory.create(
        [
            FilesystemProvider,
            GitProvider,
        ]
    )

    assert [provider.provider_type for provider in providers] == [
        ProviderType.FILESYSTEM,
        ProviderType.GIT,
    ]


def test_factory_creates_fresh_instances(
    tmp_path: Path,
) -> None:
    factory = create_factory(tmp_path)

    first = factory.create([GitProvider])
    second = factory.create([GitProvider])

    assert first[0] is not second[0]


def test_factory_rejects_unsupported_provider_class(
    tmp_path: Path,
) -> None:
    class UnsupportedProvider:
        pass

    factory = create_factory(tmp_path)

    with pytest.raises(
        ValueError,
        match="Unsupported provider class",
    ):
        factory.create([UnsupportedProvider])


def test_factory_does_not_start_provider_lifecycle(
    tmp_path: Path,
) -> None:
    factory = create_factory(tmp_path)

    providers = factory.create([GitProvider])

    assert providers[0].provider_type == ProviderType.GIT