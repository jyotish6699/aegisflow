import asyncio
from pathlib import Path

from observation.dashboard.factory import create_dashboard_app
from observation.dashboard.runtime import DashboardRuntimeBridge
from observation.dashboard.ui.app import DashboardApp


class FakeRuntime:
    workspace = Path("/home/jyotish/dev/aegisflow")


def test_create_dashboard_app_composes_runtime_bridge() -> None:
    runtime = FakeRuntime()

    app = create_dashboard_app(runtime)

    assert isinstance(app, DashboardApp)
    assert app._state.project.name == "aegisflow"
    assert app._state.project.path == runtime.workspace
    assert isinstance(app._bridge, DashboardRuntimeBridge)


def test_create_dashboard_app_uses_runtime_workspace() -> None:
    runtime = FakeRuntime()
    runtime.workspace = Path("/tmp/example-project")

    app = create_dashboard_app(runtime)

    assert app._state.project.name == "example-project"
    assert app._state.project.path == Path(
        "/tmp/example-project"
    )
