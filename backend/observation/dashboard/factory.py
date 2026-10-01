from observation.dashboard.runtime import DashboardRuntimeBridge
from observation.dashboard.state import (
    DashboardState,
    ProjectState,
)
from observation.dashboard.ui.app import DashboardApp
from observation.logging.runtime import ObservationRuntime


def create_dashboard_app(
    runtime: ObservationRuntime,
) -> DashboardApp:
    workspace = runtime.workspace

    state = DashboardState(
        project=ProjectState(
            name=workspace.name,
            path=workspace,
        )
    )

    bridge = DashboardRuntimeBridge(
        runtime=runtime,
        state=state,
    )

    return DashboardApp(
        state=state,
        bridge=bridge,
    )
