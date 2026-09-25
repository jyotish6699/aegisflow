from pathlib import Path

from observation.dashboard.state import (
    DashboardState,
    DashboardStatus,
    FilesystemProviderState,
    GitProviderState,
    ProjectState,
    ProviderStatus,
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
