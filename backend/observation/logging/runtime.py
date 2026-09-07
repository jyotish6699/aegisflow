import asyncio
from collections.abc import AsyncIterator
from pathlib import Path

from observation.core.observation import Observation
from observation.providers.filesystem.provider import FilesystemProvider
from observation.providers.git.provider import GitProvider
from observation.providers.terminal.provider import TerminalProvider


class ObservationRuntime:
    """
    Runs the Git, Terminal, and Filesystem providers concurrently
    and exposes their observations as one unified asynchronous stream.
    """

    def __init__(self, workspace: Path) -> None:
        self._workspace = workspace.resolve()

        self._terminal_protocol = (
            Path("/tmp") / "aegisflow-terminal.jsonl"
        )

        self._providers = [
            GitProvider(self._workspace),
            TerminalProvider(
                self._workspace,
                self._terminal_protocol,
            ),
            FilesystemProvider(self._workspace),
        ]

        self._started = False
        self._stopped = False

    async def initialize(self) -> None:
        """Initialize all providers."""

        for provider in self._providers:
            await provider.initialize()

    async def start(self) -> None:
        """Start all providers."""

        for provider in self._providers:
            await provider.start()

        self._started = True
        self._stopped = False

    async def observe(self) -> AsyncIterator[Observation]:
        """
        Poll all providers concurrently and yield observations
        through one unified stream.
        """

        if not self._started:
            return

        while not self._stopped:
            observations: list[Observation] = []

            async def collect(
                provider,
            ) -> list[Observation]:
                result: list[Observation] = []

                async for observation in provider.observe():
                    result.append(observation)

                return result

            results = await asyncio.gather(
                *(
                    collect(provider)
                    for provider in self._providers
                )
            )

            for provider_observations in results:
                observations.extend(provider_observations)

            for observation in observations:
                yield observation

            await asyncio.sleep(0.05)

    async def stop(self) -> None:
        """Stop all providers."""

        self._stopped = True

        for provider in reversed(self._providers):
            await provider.stop()

        self._started = False