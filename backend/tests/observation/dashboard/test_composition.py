from pathlib import Path

from observation.core.enums import ProviderType
from observation.dashboard.composition import (
    create_observation_runtime,
)
from observation.logging.runtime import ObservationRuntime


def test_create_observation_runtime_composes_all_providers(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    terminal_protocol = tmp_path / "terminal.jsonl"

    runtime = create_observation_runtime(
        workspace=workspace,
        terminal_protocol=terminal_protocol,
    )

    assert isinstance(runtime, ObservationRuntime)
    assert runtime.workspace == workspace.resolve()

    assert [
        provider.provider_type
        for provider in runtime.providers
    ] == [
        ProviderType.GIT,
        ProviderType.TERMINAL,
        ProviderType.FILESYSTEM,
    ]


def test_create_observation_runtime_uses_existing_composition_flow(
    tmp_path: Path,
) -> None:
    runtime = create_observation_runtime(
        workspace=tmp_path / "workspace",
        terminal_protocol=tmp_path / "terminal.jsonl",
    )

    assert all(
        provider is not None
        for provider in runtime.providers
    )

    assert len(runtime.providers) == 3
