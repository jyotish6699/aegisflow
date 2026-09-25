from pathlib import Path
from datetime import datetime

from observation.core.enums import ProviderType
from observation.core.metadata import ObservationMetadata
from observation.core.observation import Observation

from observation.dashboard.state import (
    DashboardState,
    DashboardStatus,
    FilesystemProviderState,
    GitProviderState,
    ObservationEntry,
    ProjectState,
    ProviderStatus,
    TerminalLogEntry,
    TerminalProviderState,
)


def test_dashboard_state_has_single_project() -> None:
    project = ProjectState(
        name="aegisflow",
        path=Path("/home/jyotish/dev/aegisflow"),
    )

    state = DashboardState(project)

    assert state.project is project
    assert state.overall_status == DashboardStatus.IDLE


def test_dashboard_state_creates_all_provider_states() -> None:
    project = ProjectState(
        name="aegisflow",
        path=Path("/home/jyotish/dev/aegisflow"),
    )

    state = DashboardState(project)

    assert isinstance(state.git, GitProviderState)
    assert isinstance(state.terminal, TerminalProviderState)
    assert isinstance(state.filesystem, FilesystemProviderState)

    assert state.git.status == ProviderStatus.IDLE
    assert state.terminal.status == ProviderStatus.IDLE
    assert state.filesystem.status == ProviderStatus.IDLE


def test_git_state_contains_branch_and_repository() -> None:
    git = GitProviderState(
        status=ProviderStatus.RUNNING,
        repository="aegisflow",
        branch="main",
    )

    assert git.provider == "git"
    assert git.status == ProviderStatus.RUNNING
    assert git.repository == "aegisflow"
    assert git.branch == "main"


def test_terminal_state_contains_session_information() -> None:
    cwd = Path("/home/jyotish/dev/aegisflow")

    terminal = TerminalProviderState(
        status=ProviderStatus.RUNNING,
        shell="zsh",
        cwd=cwd,
        active_session=True,
    )

    assert terminal.provider == "terminal"
    assert terminal.status == ProviderStatus.RUNNING
    assert terminal.shell == "zsh"
    assert terminal.cwd == cwd
    assert terminal.active_session is True


def test_filesystem_state_contains_workspace_and_event() -> None:
    workspace = Path("/home/jyotish/dev/aegisflow")

    filesystem = FilesystemProviderState(
        status=ProviderStatus.RUNNING,
        workspace=workspace,
        event_type="file.modified",
    )

    assert filesystem.provider == "filesystem"
    assert filesystem.status == ProviderStatus.RUNNING
    assert filesystem.workspace == workspace
    assert filesystem.event_type == "file.modified"


def test_dashboard_state_contains_observation_buffer() -> None:
    project = ProjectState(
        name="aegisflow",
        path=Path("/home/jyotish/dev/aegisflow"),
    )

    observation = ObservationEntry(
        timestamp=datetime.now(),
        provider="filesystem",
        observation_type="file.modified",
        rendered_message="state.py updated",
    )

    state = DashboardState(
        project=project,
        observations=[observation],
    )

    assert state.observations == [observation]
    assert state.observations[0].provider == "filesystem"
    assert state.observations[0].observation_type == "file.modified"
    assert state.observations[0].rendered_message == "state.py updated"


def test_dashboard_state_contains_terminal_log() -> None:
    project = ProjectState(
        name="aegisflow",
        path=Path("/home/jyotish/dev/aegisflow"),
    )

    log_entry = TerminalLogEntry(
        timestamp=datetime.now(),
        message="pytest tests/observation/dashboard/test_state.py",
    )

    state = DashboardState(
        project=project,
        terminal_log=[log_entry],
    )

    assert state.terminal_log == [log_entry]
    assert state.terminal_log[0].message == (
        "pytest tests/observation/dashboard/test_state.py"
    )


def test_dashboard_state_keeps_latest_observations() -> None:
    project = ProjectState(
        name="aegisflow",
        path=Path("/home/jyotish/dev/aegisflow"),
    )

    state = DashboardState(
        project=project,
        max_observations=3,
    )

    observations = [
        ObservationEntry(
            timestamp=datetime.now(),
            provider="filesystem",
            observation_type=f"file.modified.{index}",
            rendered_message=f"file-{index}.py updated",
        )
        for index in range(5)
    ]

    for observation in observations:
        state.add_observation(observation)

    assert len(state.observations) == 3
    assert state.observations == observations[-3:]


def test_dashboard_state_keeps_latest_terminal_log_entries() -> None:
    project = ProjectState(
        name="aegisflow",
        path=Path("/home/jyotish/dev/aegisflow"),
    )

    state = DashboardState(
        project=project,
        max_terminal_log=2,
    )

    entries = [
        TerminalLogEntry(
            timestamp=datetime.now(),
            message=f"command-{index}",
        )
        for index in range(4)
    ]

    for entry in entries:
        state.add_terminal_log(entry)

    assert len(state.terminal_log) == 2
    assert state.terminal_log == entries[-2:]


def test_dashboard_state_rejects_invalid_observation_limit() -> None:
    project = ProjectState(
        name="aegisflow",
        path=Path("/home/jyotish/dev/aegisflow"),
    )

    try:
        DashboardState(
            project=project,
            max_observations=0,
        )
        assert False
    except ValueError as exc:
        assert str(exc) == "max_observations must be greater than zero"


def test_dashboard_state_rejects_invalid_terminal_log_limit() -> None:
    project = ProjectState(
        name="aegisflow",
        path=Path("/home/jyotish/dev/aegisflow"),
    )

    try:
        DashboardState(
            project=project,
            max_terminal_log=0,
        )
        assert False
    except ValueError as exc:
        assert str(exc) == "max_terminal_log must be greater than zero"


def test_dashboard_state_applies_terminal_observation() -> None:
    project = ProjectState(
        name="aegisflow",
        path=Path("/home/jyotish/dev/aegisflow"),
    )

    occurred_at = datetime.now()

    observation = Observation(
        provider=ProviderType.TERMINAL,
        observation_type="command.completed",
        occurred_at=occurred_at,
        metadata=ObservationMetadata(
            source="terminal",
            attributes={
                "command": "pytest tests/observation/dashboard",
                "cwd": "/home/jyotish/dev/aegisflow",
                "exit_code": 0,
            },
        ),
    )

    state = DashboardState(project=project)

    state.apply_observation(observation)

    assert len(state.observations) == 1
    assert (
        state.observations[0].rendered_message
        == "pytest tests/observation/dashboard executed successfully"
    )

    assert len(state.terminal_log) == 1
    assert (
        state.terminal_log[0].message
        == "pytest tests/observation/dashboard executed successfully"
    )

    assert state.terminal.cwd == Path(
        "/home/jyotish/dev/aegisflow"
    )
    assert state.terminal.active_session is True
    assert state.terminal.last_activity == occurred_at


def test_dashboard_state_renders_failed_terminal_command() -> None:
    project = ProjectState(
        name="aegisflow",
        path=Path("/home/jyotish/dev/aegisflow"),
    )

    observation = Observation(
        provider=ProviderType.TERMINAL,
        observation_type="command.completed",
        metadata=ObservationMetadata(
            source="terminal",
            attributes={
                "command": "pytest",
                "cwd": "/home/jyotish/dev/aegisflow",
                "exit_code": 1,
            },
        ),
    )

    state = DashboardState(project=project)

    state.apply_observation(observation)

    assert (
        state.observations[0].rendered_message
        == "pytest failed (exit code 1)"
    )

    assert (
        state.terminal_log[0].message
        == "pytest failed (exit code 1)"
    )


def test_dashboard_state_applies_filesystem_observation() -> None:
    project = ProjectState(
        name="aegisflow",
        path=Path("/home/jyotish/dev/aegisflow"),
    )

    occurred_at = datetime.now()

    observation = Observation(
        provider=ProviderType.FILESYSTEM,
        observation_type="file.modified",
        occurred_at=occurred_at,
        metadata=ObservationMetadata(
            source="filesystem",
            attributes={
                "workspace": "/home/jyotish/dev/aegisflow",
                "path": (
                    "/home/jyotish/dev/aegisflow/"
                    "backend/observation/dashboard/state.py"
                ),
            },
        ),
    )

    state = DashboardState(project=project)

    state.apply_observation(observation)

    assert (
        state.observations[0].rendered_message
        == (
            "/home/jyotish/dev/aegisflow/"
            "backend/observation/dashboard/state.py updated"
        )
    )

    assert state.filesystem.workspace == Path(
        "/home/jyotish/dev/aegisflow"
    )
    assert state.filesystem.event_type == "file.modified"
    assert state.filesystem.last_activity == occurred_at


def test_dashboard_state_applies_git_branch_observation() -> None:
    project = ProjectState(
        name="aegisflow",
        path=Path("/home/jyotish/dev/aegisflow"),
    )

    occurred_at = datetime.now()

    observation = Observation(
        provider=ProviderType.GIT,
        observation_type="branch.changed",
        occurred_at=occurred_at,
        metadata=ObservationMetadata(
            source="git",
            attributes={
                "workspace": "/home/jyotish/dev/aegisflow",
                "repository": "/home/jyotish/dev/aegisflow",
                "branch": "feature/observation-dashboard-v0",
            },
        ),
    )

    state = DashboardState(project=project)

    state.apply_observation(observation)

    assert (
        state.git.branch
        == "feature/observation-dashboard-v0"
    )

    assert (
        state.git.repository
        == "/home/jyotish/dev/aegisflow"
    )

    assert state.git.last_activity == occurred_at

    assert (
        state.observations[0].rendered_message
        == "feature/observation-dashboard-v0 changed"
    )


