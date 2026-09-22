import asyncio
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static

from textual.message import Message

from observation.core.enums import ProviderType
from observation.core.observation import Observation
from observation.composition.composer import ProviderComposer
from observation.composition.factory import ProviderFactory
from observation.config.settings import ObservationSettings
from observation.lifecycle.health import ProviderHealthTracker
from observation.lifecycle.loader import ProviderLoader
from observation.lifecycle.starter import ProviderStarter
from observation.lifecycle.stopper import ProviderStopper
from observation.providers.filesystem.provider import FilesystemProvider
from observation.providers.git.provider import GitProvider
from observation.providers.terminal.provider import TerminalProvider
from observation.registry.discovery import discover_providers
from observation.registry.registry import ProviderRegistry
from observation.logging.runtime import ObservationRuntime
from observation.core.metadata import ObservationMetadata


class ObservationPanel(Static):
    """Live observation log for one provider."""

    def __init__(self, title: str, **kwargs) -> None:
        super().__init__(title, **kwargs)

        self._title = title
        self._lines: list[str] = []

    def add_observation(self, observation: Observation) -> None:
        line = (
            f"[{observation.occurred_at:%H:%M:%S}] "
            f"{observation.observation_type}"
        )

        self._lines.append(line)

        self.update(
            f"{self._title}\n\n" +
            "\n".join(self._lines)
        )

        self.scroll_end(animate=False)


class ObservationMessage(Message):
    """Message carrying one observation to the UI."""

    def __init__(self, observation: Observation) -> None:
        self.observation = observation
        super().__init__()

class ObservationLoggingApp(App):
    """Display live observations from all three providers."""

    TITLE = "AegisFlow Observation Logging"

    CSS = """
    Horizontal {
        width: 100%;
        height: 100%;
    }

    .provider {
        width: 1fr;
        height: 100%;
        border: solid white;
        padding: 1 2;
        overflow-y: auto;
    }
    """

    def __init__(self) -> None:
        super().__init__()

        workspace = Path.home() / "dev" / "aegisflow"
        terminal_protocol = Path("/tmp/aegisflow-terminal.jsonl")

        discovered = discover_providers(
            [
                GitProvider,
                TerminalProvider,
                FilesystemProvider,
            ]
        )

        registry = ProviderRegistry()

        factory = ProviderFactory(
            workspace,
            terminal_protocol,
        )

        composer = ProviderComposer(
            factory,
            registry,
        )

        composer.compose(discovered)

        settings = ObservationSettings(
            enabled=True,
            providers=[
                ProviderType.GIT,
                ProviderType.TERMINAL,
                ProviderType.FILESYSTEM,
            ],
        )

        loader = ProviderLoader(
            registry,
            settings,
        )

        providers = loader.load()

        health = ProviderHealthTracker()

        starter = ProviderStarter(health)
        stopper = ProviderStopper(health)

        self._runtime = ObservationRuntime(
            workspace,
            providers,
            starter,
            stopper,
        )

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield ObservationPanel(
                "GIT",
                classes="provider",
                id="git",
            )

            yield ObservationPanel(
                "TERMINAL",
                classes="provider",
                id="terminal",
            )

            yield ObservationPanel(
                "FILESYSTEM",
                classes="provider",
                id="filesystem",
            )

    async def on_mount(self) -> None:

        await self._runtime.start()

        self.run_worker(
            self._consume_observations,
            name="observation-consumer",
        )

    async def _consume_observations(self) -> None:
        git_panel = self.query_one("#git", ObservationPanel)

        git_panel.update(
            "GIT\n\n"
            "1. mount\n"
            "2. initialized\n"
            "3. started\n"
            "4. worker created\n"
            "5. consumer entered"
        )

        async for observation in self._runtime.observe():
            self._display_observation(observation)


    def on_observation_message(
        self,
        message: ObservationMessage,
    ) -> None:
        self._display_observation(message.observation)

    def _display_observation(self, observation: Observation) -> None:
        print(
            "DISPLAY:",
            observation.provider.value,
            observation.observation_type,
        )

        panel_ids = {
            ProviderType.GIT: "git",
            ProviderType.TERMINAL: "terminal",
            ProviderType.FILESYSTEM: "filesystem",
        }

        panel_id = panel_ids.get(observation.provider)

        if panel_id is None:
            return

        panel = self.query_one(
            f"#{panel_id}",
            ObservationPanel,
        )

        panel.add_observation(observation)

    async def on_unmount(self) -> None:
        await self._runtime.stop()


if __name__ == "__main__":
    ObservationLoggingApp().run()
