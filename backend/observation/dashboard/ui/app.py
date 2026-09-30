from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Static

from observation.dashboard.runtime import DashboardRuntimeBridge
from observation.dashboard.state import (
    DashboardState,
    DashboardStatus,
    ProjectState,
    ProviderStatus,
)


class DashboardApp(App):
    TITLE = "AegisFlow Observation Dashboard"

    CSS = """
    Screen {
        layout: vertical;
    }

    #project-header {
        height: 9;
        border: round $accent;
        padding: 1 2;
    }

    #project-name {
        text-style: bold;
        height: 1;
    }

    #project-subtitle {
        color: $text-muted;
        height: 1;
        margin-bottom: 1;
    }

    #project-info {
        height: 5;
    }

    #project-title {
        width: 1fr;
        text-style: bold;
    }

    #overall-status {
        width: auto;
        text-style: bold;
        padding: 0 2;
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

    def __init__(
        self,
        state: DashboardState,
        bridge: DashboardRuntimeBridge | None = None,
    ) -> None:
        super().__init__()

        self._state = state
        self._bridge = bridge
        self._refresh_timer = None

    def compose(self) -> ComposeResult:
        yield Header()

        with Vertical(id="project-header"):
            yield Static(
                "AEGISFLOW",
                id="project-name",
            )

            yield Static(
                "Real-time Project Observation",
                id="project-subtitle",
            )

            yield Static(
                self._project_text(),
                id="project-info",
            )

            yield Static(
                self._overall_status_text(),
                id="overall-status",
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

    async def on_mount(self) -> None:
        if self._bridge is None:
            return

        await self._bridge.start()

        self._refresh_timer = self.set_interval(
            0.1,
            self.refresh_state,
        )

    async def on_unmount(self) -> None:
        if self._refresh_timer is not None:
            self._refresh_timer.pause()
            self._refresh_timer = None

        if self._bridge is not None:
            await self._bridge.stop()

    def refresh_state(self) -> None:
        self.query_one("#project-info", Static).update(
            self._project_text()
        )

        self.query_one("#overall-status", Static).update(
            self._overall_status_text()
        )

        self.query_one("#git-provider", Static).update(
            self._git_text()
        )

        self.query_one("#terminal-provider", Static).update(
            self._terminal_text()
        )

        self.query_one("#filesystem-provider", Static).update(
            self._filesystem_text()
        )

        self.query_one("#observations", Static).update(
            self._observation_text()
        )

        self.query_one("#terminal-log", Static).update(
            self._terminal_log_text()
        )

    def _project_text(self) -> str:
        project = self._state.project

        repository = project.repository or "--"
        branch = self._state.git.branch or "--"
        status = self._state.overall_status.value.upper()

        return (
            f"Project    {project.name}\n"
            f"Path       {project.path}\n"
            f"Repository {repository}\n"
            f"Branch     {branch}\n"
            f"Status     {status}"
        )

    def _overall_status_text(self) -> str:
        return f"● {self._state.overall_status.value.upper()}"

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
            entry.message
            if hasattr(entry, "message")
            else str(entry)
            for entry in self._state.terminal_log
        )

    @staticmethod
    def _status_text(status: ProviderStatus) -> str:
        return status.value.upper()


if __name__ == "__main__":
    state = DashboardState(
        project=ProjectState(
            name=Path.cwd().name,
            path=Path.cwd(),
        ),
        overall_status=DashboardStatus.IDLE,
    )

    DashboardApp(state).run()
    