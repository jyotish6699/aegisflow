from datetime import datetime
from pathlib import Path

from observation.core.enums import ProviderType
from observation.core.metadata import ObservationMetadata
from observation.core.observation import Observation
from observation.dashboard.adapter import DashboardObservationAdapter
from observation.dashboard.state import (
    DashboardState,
    ProjectState,
)


def create_state() -> DashboardState:
    return DashboardState(
        project=ProjectState(
            name="aegisflow",
            path=Path("/home/jyotish/dev/aegisflow"),
        )
    )


def create_observation(
    provider: ProviderType,
    observation_type: str,
    attributes: dict,
) -> Observation:
    return Observation(
        provider=provider,
        observation_type=observation_type,
        occurred_at=datetime.now(),
        metadata=ObservationMetadata(
            source="test",
            attributes=attributes,
        ),
    )


def test_adapter_applies_observation_to_dashboard_state() -> None:
    state = create_state()
    adapter = DashboardObservationAdapter(state)

    observation = create_observation(
        ProviderType.FILESYSTEM,
        "file.modified",
        {
            "workspace": "/home/jyotish/dev/aegisflow",
            "path": "README.md",
        },
    )

    adapter.apply(observation)

    assert len(state.observations) == 1
    assert (
        state.observations[0].observation_type
        == "file.modified"
    )
    assert (
        state.observations[0].rendered_message
        == "README.md updated"
    )


def test_adapter_applies_terminal_observation() -> None:
    state = create_state()
    adapter = DashboardObservationAdapter(state)

    observation = create_observation(
        ProviderType.TERMINAL,
        "command.completed",
        {
            "command": "pytest",
            "cwd": "/home/jyotish/dev/aegisflow/backend",
            "exit_code": 0,
        },
    )

    adapter.apply(observation)

    assert len(state.observations) == 1
    assert len(state.terminal_log) == 1
    assert (
        state.terminal_log[0].message
        == "pytest executed successfully"
    )


def test_adapter_applies_git_observation() -> None:
    state = create_state()
    adapter = DashboardObservationAdapter(state)

    observation = create_observation(
        ProviderType.GIT,
        "branch.changed",
        {
            "branch": "feature/observation-dashboard-v0",
        },
    )

    adapter.apply(observation)

    assert state.git.branch == (
        "feature/observation-dashboard-v0"
    )
    assert len(state.observations) == 1
    assert (
        state.observations[0].rendered_message
        == "feature/observation-dashboard-v0 changed"
    )
    