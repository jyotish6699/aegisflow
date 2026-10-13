import asyncio
import subprocess
from datetime import datetime
from pathlib import Path

import pytest

from observation.core.enums import ProviderType
from observation.core.metadata import ObservationMetadata
from observation.core.observation import Observation
from observation.lifecycle.health import ProviderHealth
from observation.dashboard.runtime import DashboardRuntimeBridge
from observation.dashboard.state import (
    DashboardStatus,
    DashboardState,
    ProjectState,
    ProviderStatus,
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

    def provider_health(self):
        return {}

    async def lifecycle_events(self):
        if False:
            yield {}


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
async def test_bridge_delivers_terminal_output_to_dashboard_state() -> None:
    observations = [
        create_observation(
            ProviderType.TERMINAL,
            "command.started",
            {
                "command_id": "command-1",
                "command": "printf",
                "cwd": "/home/jyotish/dev/aegisflow",
                "session_id": "session-1",
                "sequence": 1,
            },
        ),
        create_observation(
            ProviderType.TERMINAL,
            "terminal.output",
            {
                "command_id": "command-1",
                "cwd": "/home/jyotish/dev/aegisflow",
                "session_id": "session-1",
                "sequence": 2,
                "stream": "stdout",
                "text": "hello\n",
            },
        ),
        create_observation(
            ProviderType.TERMINAL,
            "terminal.output",
            {
                "command_id": "command-1",
                "cwd": "/home/jyotish/dev/aegisflow",
                "session_id": "session-1",
                "sequence": 3,
                "stream": "stderr",
                "text": "error\n",
            },
        ),
        create_observation(
            ProviderType.TERMINAL,
            "command.completed",
            {
                "command_id": "command-1",
                "command": "printf",
                "cwd": "/home/jyotish/dev/aegisflow",
                "session_id": "session-1",
                "sequence": 4,
                "exit_code": 0,
            },
        ),
    ]

    state = create_state()
    await DashboardRuntimeBridge(
        FakeRuntime(observations),
        state,
    ).consume()

    assert [
        entry.rendered_message for entry in state.observations
    ] == [
        "printf started",
        "[stdout] hello\n",
        "[stderr] error\n",
        "printf executed successfully",
    ]


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
@pytest.mark.parametrize(
    ("git", "terminal", "filesystem", "overall"),
    [
        (
            ProviderHealth.RUNNING,
            ProviderHealth.STOPPED,
            ProviderHealth.STOPPED,
            "running",
        ),
        (
            ProviderHealth.STOPPED,
            ProviderHealth.RUNNING,
            ProviderHealth.STOPPED,
            "running",
        ),
        (
            ProviderHealth.STOPPED,
            ProviderHealth.STOPPED,
            ProviderHealth.RUNNING,
            "running",
        ),
        (
            ProviderHealth.STOPPED,
            ProviderHealth.STOPPED,
            ProviderHealth.STOPPED,
            "idle",
        ),
    ],
)
async def test_bridge_syncs_initial_provider_health(
    git: ProviderHealth,
    terminal: ProviderHealth,
    filesystem: ProviderHealth,
    overall: str,
) -> None:
    class Runtime(FakeRuntime):
        def provider_health(self):
            return {
                ProviderType.GIT: git,
                ProviderType.TERMINAL: terminal,
                ProviderType.FILESYSTEM: filesystem,
            }

        async def start(self) -> None:
            return

        async def stop(self) -> None:
            return

    state = create_state()
    bridge = DashboardRuntimeBridge(Runtime([]), state)

    await bridge.start()

    assert state.git.status.value == (
        "running" if git == ProviderHealth.RUNNING else "idle"
    )
    assert state.terminal.status.value == (
        "running" if terminal == ProviderHealth.RUNNING else "idle"
    )
    assert state.filesystem.status.value == (
        "running"
        if filesystem == ProviderHealth.RUNNING
        else "idle"
    )
    assert state.overall_status.value == overall

    await bridge.stop()


@pytest.mark.asyncio
async def test_bridge_reflects_failed_provider_without_stopping_others() -> None:
    class Runtime(FakeRuntime):
        def provider_health(self):
            return {
                ProviderType.GIT: ProviderHealth.RUNNING,
                ProviderType.TERMINAL: ProviderHealth.RUNNING,
                ProviderType.FILESYSTEM: ProviderHealth.STOPPED,
            }

        async def start(self) -> None:
            return

        async def stop(self) -> None:
            return

        async def lifecycle_events(self):
            yield {
                ProviderType.GIT: ProviderHealth.FAILED,
                ProviderType.TERMINAL: ProviderHealth.RUNNING,
                ProviderType.FILESYSTEM: ProviderHealth.STOPPED,
            }

    state = create_state()
    bridge = DashboardRuntimeBridge(Runtime([]), state)

    await bridge.start()
    await asyncio.sleep(0)

    assert state.git.status.value == "idle"
    assert state.git.reason == "provider failed"
    assert state.terminal.status.value == "running"
    assert state.overall_status.value == "running"

    await bridge.stop()


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

    assert state.filesystem.status == ProviderStatus.RUNNING
    assert state.terminal.status == ProviderStatus.RUNNING
    assert state.overall_status == DashboardStatus.RUNNING

    target = workspace / "dashboard_probe.txt"
    target.write_text("aegisflow")

    for _ in range(200):
        if any(
            observation.observation_type == "file.created"
            for observation in state.observations
        ):
            break

        await asyncio.sleep(0.02)

    await bridge.stop()

    assert state.filesystem.status == ProviderStatus.IDLE
    assert state.terminal.status == ProviderStatus.IDLE
    assert state.overall_status == DashboardStatus.IDLE

    assert any(
        observation.observation_type == "file.created"
        for observation in state.observations
    )

    assert any(
        observation.rendered_message
        == f"{target} new created"
        for observation in state.observations
    )


@pytest.mark.asyncio
async def test_bridge_consumes_real_git_observation(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()

    subprocess.run(
        ["git", "init", str(repository)],
        check=True,
        capture_output=True,
        text=True,
    )

    terminal_protocol = tmp_path / "terminal.jsonl"

    runtime = create_observation_runtime(
        workspace=repository,
        terminal_protocol=terminal_protocol,
    )

    state = DashboardState(
        project=ProjectState(
            name=repository.name,
            path=repository,
        )
    )

    bridge = DashboardRuntimeBridge(
        runtime=runtime,
        state=state,
    )

    await bridge.start()

    for _ in range(200):
        if any(
            observation.observation_type
            == "repository.detected"
            for observation in state.observations
        ):
            break

        await asyncio.sleep(0.02)

    await bridge.stop()

    assert any(
        observation.observation_type
        == "repository.detected"
        for observation in state.observations
    )

    assert any(
        observation.rendered_message
        == f"{repository.resolve()} repository detected"
        for observation in state.observations
    )

    assert state.git.repository == str(
        repository.resolve()
    )


@pytest.mark.asyncio
async def test_bridge_consumes_real_terminal_observation(
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

    terminal_protocol.write_text(
        '{"type":"command.completed",'
        '"command_id":"test-command",'
        '"command":"echo hello",'
        f'"cwd":"{workspace}",'
        '"exit_code":0,'
        '"duration":0.01}\n'
    )

    for _ in range(50):
        if any(
            observation.observation_type
            == "command.completed"
            for observation in state.observations
        ):
            break

        await asyncio.sleep(0.02)

    await bridge.stop()

    assert any(
        observation.observation_type
        == "command.completed"
        for observation in state.observations
    )

    assert any(
        observation.rendered_message
        == "echo hello executed successfully"
        for observation in state.observations
    )
    