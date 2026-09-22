import asyncio
from collections.abc import AsyncIterator
from pathlib import Path

from observation.core.observation import Observation
from observation.core.provider import ObservationProvider
from observation.lifecycle.starter import ProviderStarter
from observation.lifecycle.stopper import ProviderStopper

class ObservationRuntime:
    """
    Runs the Git, Terminal, and Filesystem providers concurrently
    and exposes their observations as one unified asynchronous stream.
    """

    def __init__(
        self,
        workspace: Path,
        providers: list[ObservationProvider],
        starter: ProviderStarter,
        stopper: ProviderStopper,
    ) -> None:
        self._workspace = workspace.resolve()
        self._providers = providers
        self._starter = starter
        self._stopper = stopper

        self._started = False
        self._stopped = False

    @property
    def workspace(self) -> Path:
        """Return the workspace owned by this runtime."""
        return self._workspace

    @property
    def providers(self) -> list[ObservationProvider]:
        """Return the providers owned by this runtime session."""
        return self._providers

    async def start(self) -> None:
        """Start providers through the lifecycle coordinator."""

        started_providers = await self._starter.start_all(
            self._providers
        )

        self._providers = started_providers
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
        """Stop providers through the lifecycle coordinator."""

        self._stopped = True

        stopped_providers = await self._stopper.stop_all(
            self._providers
        )

        self._providers = stopped_providers
        self._started = False

