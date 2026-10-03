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
from observation.dashboard.composition import (
    create_observation_runtime,
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


@pytest.mark.asyncio
async def test_bridge_starts_and_stops_runtime() -> None:
    class LifecycleRuntime(FakeRuntime):
        def __init__(self) -> None:
            super().__init__([])
            self.started = False
            self.stopped = False

        async def start(self) -> None:
            self.started = True

        async def stop(self) -> None:
            self.stopped = True

    runtime = LifecycleRuntime()
    state = create_state()

    bridge = DashboardRuntimeBridge(
        runtime=runtime,
        state=state,
    )

    await bridge.start()

    assert runtime.started is True

    await bridge.stop()

    assert runtime.stopped is True


@pytest.mark.asyncio
async def test_bridge_consumes_real_filesystem_observation(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    terminal_protocol = tmp_path / "terminal.jsonl"

    runtime = create_observation_runtime(
        workspace=workspace,
        terminal_protocol=terminal_protocol,
    )

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

    await bridge.start()

    target = workspace / "dashboard_probe.txt"
    target.write_text("aegisflow")

    for _ in range(50):
        if any(
            observation.observation_type == "file.created"
            for observation in state.observations
        ):
            break

        await asyncio.sleep(0.02)

    await bridge.stop()

    assert any(
        observation.observation_type == "file.created"
        for observation in state.observations
    )

    assert any(
        observation.rendered_message
        == f"{target} new created"
        for observation in state.observations
    )
    