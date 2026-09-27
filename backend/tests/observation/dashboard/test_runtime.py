import asyncio
from datetime import datetime
from pathlib import Path

import pytest

from observation.core.enums import ProviderType
from observation.core.metadata import ObservationMetadata
from observation.core.observation import Observation
from observation.dashboard.runtime import DashboardRuntimeBridge
from observation.dashboard.state import (
    DashboardState,
    ProjectState,
)


class FakeRuntime:
    def __init__(self, observations):
        self._observations = observations

    async def observe(self):
        for observation in self._observations:
            yield observation
            await asyncio.sleep(0)


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


def create_state() -> DashboardState:
    return DashboardState(
        project=ProjectState(
            name="aegisflow",
            path=Path("/home/jyotish/dev/aegisflow"),
        )
    )


@pytest.mark.asyncio
async def test_bridge_consumes_runtime_observations() -> None:
    observation = create_observation(
        ProviderType.FILESYSTEM,
        "file.modified",
        {
            "workspace": "/home/jyotish/dev/aegisflow",
            "path": "README.md",
        },
    )

    runtime = FakeRuntime([observation])
    state = create_state()

    bridge = DashboardRuntimeBridge(
        runtime=runtime,
        state=state,
    )

    await bridge.consume()

    assert len(state.observations) == 1
    assert (
        state.observations[0].rendered_message
        == "README.md updated"
    )


@pytest.mark.asyncio
async def test_bridge_processes_multiple_runtime_observations() -> None:
    observations = [
        create_observation(
            ProviderType.TERMINAL,
            "command.completed",
            {
                "command": "pytest",
                "cwd": "/home/jyotish/dev/aegisflow/backend",
                "exit_code": 0,
            },
        ),
        create_observation(
            ProviderType.FILESYSTEM,
            "file.modified",
            {
                "workspace": "/home/jyotish/dev/aegisflow",
                "path": "README.md",
            },
        ),
        create_observation(
            ProviderType.GIT,
            "branch.changed",
            {
                "branch": "main",
            },
        ),
    ]

    runtime = FakeRuntime(observations)
    state = create_state()

    bridge = DashboardRuntimeBridge(
        runtime=runtime,
        state=state,
    )

    await bridge.consume()

    assert len(state.observations) == 3

    assert (
        state.observations[0].rendered_message
        == "pytest executed successfully"
    )

    assert (
        state.observations[1].rendered_message
        == "README.md updated"
    )

    assert (
        state.observations[2].rendered_message
        == "main changed"
    )

    assert state.git.branch == "main"
    