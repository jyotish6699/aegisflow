import asyncio
from collections.abc import AsyncIterator
from pathlib import Path

from observation.core.observation import Observation
from observation.core.provider import ObservationProvider
from observation.lifecycle.starter import ProviderStarter
from observation.lifecycle.stopper import ProviderStopper


class ObservationRuntime:
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
        self._observation_queue: asyncio.Queue[Observation] = asyncio.Queue()
        self._observation_tasks: list[asyncio.Task[None]] = []

    @property
    def workspace(self) -> Path:
        """Return the workspace owned by this runtime."""
        return self._workspace

    @property
    def providers(self) -> list[ObservationProvider]:
        """Return the providers owned by this runtime session."""
        return self._providers

    async def start(self) -> None:
        started_providers = await self._starter.start_all(
            self._providers
        )

        self._providers = started_providers
        self._started = True
        self._stopped = False

        self._observation_queue = asyncio.Queue()

        self._observation_tasks = [
            asyncio.create_task(
                self._observe_provider(provider)
            )
            for provider in self._providers
        ]

    async def _observe_provider(
        self,
        provider: ObservationProvider,
    ) -> None:
        try:
            async for observation in provider.observe():
                await self._observation_queue.put(observation)
        except asyncio.CancelledError:
            raise
        except Exception:
            return

    async def observe(self) -> AsyncIterator[Observation]:
        if not self._started:
            return

        while not self._stopped:
            observation = await self._observation_queue.get()
            yield observation

    async def stop(self) -> None:
        self._stopped = True

        for task in self._observation_tasks:
            task.cancel()

        if self._observation_tasks:
            await asyncio.gather(
                *self._observation_tasks,
                return_exceptions=True,
            )

        self._observation_tasks = []

        stopped_providers = await self._stopper.stop_all(
            self._providers
        )

        self._providers = stopped_providers
        self._started = False
