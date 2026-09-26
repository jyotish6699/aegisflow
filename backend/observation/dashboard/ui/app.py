from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Static

from observation.dashboard.state import (
    DashboardState,
    DashboardStatus,
    ProviderStatus,
)


class DashboardApp(App):
    TITLE = "AegisFlow Observation Dashboard"

    CSS = """
    Screen {
        layout: vertical;
    }

    #project-header {
        height: 7;
        border: round $accent;
        padding: 1 2;
    }

    #provider-status {
        height: 8;
        border: round $accent;
        padding: 1 2;
    }

    #provider-cards {
        height: 100%;
    }

    .provider-card {
        width: 1fr;
        border: round $panel;
        padding: 1 2;
    }

    #observation-area {
        height: 1fr;
    }

    #observations {
        height: 1fr;
        border: round $accent;
        padding: 1 2;
        overflow-y: auto;
    }

    #terminal-area {
        height: 1fr;
    }

    #terminal-log {
        height: 1fr;
        border: round $accent;
        padding: 1 2;
        overflow-y: auto;
    }

    .section-title {
        text-style: bold;
        margin-bottom: 1;
    }
    """

    def __init__(self, state: DashboardState) -> None:
        super().__init__()
        self._state = state

    def compose(self) -> ComposeResult:
        yield Header()

        with Vertical(id="project-header"):
            yield Static(
                "AEGISFLOW\n"
                "Real-time Project Observation",
                classes="section-title",
            )
            yield Static(
                self._project_text(),
                id="project-info",
            )

        with Vertical(id="provider-status"):
            yield Static(
                "PROVIDER STATUS",
                classes="section-title",
            )

            with Horizontal(id="provider-cards"):
                yield Static(
                    self._git_text(),
                    id="git-provider",
                    classes="provider-card",
                )

                yield Static(
                    self._terminal_text(),
                    id="terminal-provider",
                    classes="provider-card",
                )

                yield Static(
                    self._filesystem_text(),
                    id="filesystem-provider",
                    classes="provider-card",
                )

        with Vertical(id="observation-area"):
            yield Static(
                "LIVE OBSERVATIONS",
                classes="section-title",
            )
            yield Static(
                self._observation_text(),
                id="observations",
            )

        with Vertical(id="terminal-area"):
            yield Static(
                "TERMINAL LIVE LOG",
                classes="section-title",
            )
            yield Static(
                self._terminal_log_text(),
                id="terminal-log",
            )

        yield Footer()

    def _project_text(self) -> str:
        project = self._state.project

        repository = project.repository or "--"

        return (
            f"Project: {project.name}\n"
            f"Path: {project.path}\n"
            f"Repository: {repository}\n"
            f"Branch: {self._state.git.branch or '--'}\n"
            f"Overall: {self._state.overall_status.value.upper()}"
        )

    def _git_text(self) -> str:
        return (
            "Git Provider\n"
            f"● {self._status_text(self._state.git.status)}\n"
            f"Repository: {self._state.git.repository or '--'}\n"
            f"Branch: {self._state.git.branch or '--'}"
        )

    def _terminal_text(self) -> str:
        terminal = self._state.terminal

        cwd = str(terminal.cwd) if terminal.cwd else "--"
        shell = terminal.shell or "--"
        session = "YES" if terminal.active_session else "NO"

        return (
            "Terminal Provider\n"
            f"● {self._status_text(terminal.status)}\n"
            f"Shell: {shell}\n"
            f"CWD: {cwd}\n"
            f"Active session: {session}"
        )

    def _filesystem_text(self) -> str:
        filesystem = self._state.filesystem

        workspace = (
            str(filesystem.workspace)
            if filesystem.workspace
            else "--"
        )

        event = filesystem.event_type or "--"

        return (
            "Filesystem Provider\n"
            f"● {self._status_text(filesystem.status)}\n"
            f"Workspace: {workspace}\n"
            f"Event: {event}"
        )

    def _observation_text(self) -> str:
        if not self._state.observations:
            return "Waiting for observations..."

        return "\n".join(
            observation.rendered_message
            for observation in self._state.observations
        )

    def _terminal_log_text(self) -> str:
        if not self._state.terminal_log:
            return "Waiting for terminal output..."

        return "\n".join(
            entry
            for entry in self._state.terminal_log
        )

    @staticmethod
    def _status_text(status: ProviderStatus) -> str:
        return status.value.upper()


if __name__ == "__main__":
    from pathlib import Path

    from observation.dashboard.state import ProjectState

    state = DashboardState(
        project=ProjectState(
            name=Path.cwd().name,
            path=Path.cwd(),
        ),
        overall_status=DashboardStatus.IDLE,
    )

    DashboardApp(state).run()
