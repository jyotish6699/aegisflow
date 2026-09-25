from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Static


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

    #observations {
        height: 1fr;
        border: round $accent;
        padding: 1 2;
        overflow-y: auto;
    }

    #terminal-log {
        height: 1fr;
        border: round $accent;
        padding: 1 2;
        overflow-y: auto;
    }

    #observation-area {
        height: 1fr;
    }

    #terminal-area {
        height: 1fr;
    }

    .section-title {
        text-style: bold;
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()

        with Vertical(id="project-header"):
            yield Static(
                "AEGISFLOW\n"
                "Real-time Project Observation",
                classes="section-title",
            )
            yield Static(
                "Project: --\n"
                "Path: --\n"
                "Branch: --\n"
                "Overall: IDLE",
                id="project-info",
            )

        with Vertical(id="provider-status"):
            yield Static(
                "PROVIDER STATUS",
                classes="section-title",
            )

            with Horizontal(id="provider-cards"):
                yield Static(
                    "Git Provider\n● IDLE",
                    id="git-provider",
                    classes="provider-card",
                )

                yield Static(
                    "Terminal Provider\n● IDLE",
                    id="terminal-provider",
                    classes="provider-card",
                )

                yield Static(
                    "Filesystem Provider\n● IDLE",
                    id="filesystem-provider",
                    classes="provider-card",
                )

        with Vertical(id="observation-area"):
            yield Static(
                "LIVE OBSERVATIONS",
                classes="section-title",
            )
            yield Static(
                "Waiting for observations...",
                id="observations",
            )

        with Vertical(id="terminal-area"):
            yield Static(
                "TERMINAL LIVE LOG",
                classes="section-title",
            )
            yield Static(
                "Waiting for terminal output...",
                id="terminal-log",
            )

        yield Footer()


if __name__ == "__main__":
    DashboardApp().run()
