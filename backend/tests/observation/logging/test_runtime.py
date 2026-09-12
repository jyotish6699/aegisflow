from pathlib import Path

from observation.logging.runtime import ObservationRuntime


def test_runtime_owns_resolved_workspace(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"

    runtime = ObservationRuntime(workspace)

    assert runtime.workspace == workspace.resolve()