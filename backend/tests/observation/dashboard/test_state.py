from pathlib import Path
from datetime import datetime

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

