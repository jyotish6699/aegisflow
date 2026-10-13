import asyncio
from collections.abc import AsyncIterator
from pathlib import Path

from observation.core.observation import Observation
from observation.core.provider import ObservationProvider
from observation.core.enums import ProviderType
from observation.lifecycle.health import (
    ProviderHealth,
    ProviderHealthTracker,
)
from observation.lifecycle.starter import ProviderStarter
from observation.lifecycle.stopper import ProviderStopper


class ObservationRuntime:
    def __init__(
        self,
        workspace: Path,
        providers: list[ObservationProvider],
        starter: ProviderStarter,
        stopper: ProviderStopper,
        health: ProviderHealthTracker | None = None,
    ) -> None:
        self._workspace = workspace.resolve()
        self._providers = providers
        self._starter = starter
        self._stopper = stopper
        self._health = health or self._lifecycle_health()
        self._provider_types = {
            provider.provider_type
            for provider in providers
        }
        self._stop_event = asyncio.Event()
        self._started = False
        self._stopped = False
        self._observation_queue: asyncio.Queue[Observation | None] = (
            asyncio.Queue()
        )
        self._observation_tasks: list[asyncio.Task[None]] = []
        self._status_queue: asyncio.Queue[
            dict[ProviderType, ProviderHealth]
        ] = asyncio.Queue()

    def _lifecycle_health(self) -> ProviderHealthTracker:
        starter_health = getattr(self._starter, "health", None)

        if isinstance(starter_health, ProviderHealthTracker):
            return starter_health

        stopper_health = getattr(self._stopper, "health", None)

        if isinstance(stopper_health, ProviderHealthTracker):
            return stopper_health

        return ProviderHealthTracker()

    @property
    def workspace(self) -> Path:
        """Return the workspace owned by this runtime."""
        return self._workspace

    @property
    def providers(self) -> list[ObservationProvider]:
        """Return the providers owned by this runtime session."""
        return self._providers

    def provider_health(
        self,
    ) -> dict[ProviderType, ProviderHealth]:
        """Return a copy of the current provider lifecycle state."""
        states = self._health.snapshot()
        provider_types = self._provider_types | set(states)

        return {
            provider_type: states.get(
                provider_type,
                ProviderHealth.STOPPED,
            )
            for provider_type in provider_types
        }

    async def lifecycle_events(
        self,
    ):
        """Yield lifecycle snapshots whenever provider state changes."""
        while not self._stopped:
            yield await self._status_queue.get()

    async def _publish_lifecycle(self) -> None:
        await self._status_queue.put(self.provider_health())

    async def start(self) -> None:
        started_providers = await self._starter.start_all(
            self._providers
        )

        self._providers = started_providers
        self._started = True
        self._stopped = False
        self._stop_event = asyncio.Event()

        self._observation_queue = asyncio.Queue()
        self._status_queue = asyncio.Queue()
        await self._publish_lifecycle()

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
            self._health.set_state(
                provider.provider_type,
                ProviderHealth.FAILED,
            )
        else:
            self._health.set_state(
                provider.provider_type,
                ProviderHealth.STOPPED,
            )

        await self._publish_lifecycle()

    async def observe(self) -> AsyncIterator[Observation]:
        if not self._started:
            return

        while not self._stopped:
            observation_task = asyncio.create_task(
                self._observation_queue.get()
            )
            stop_task = asyncio.create_task(
                self._stop_event.wait()
            )

            done, pending = await asyncio.wait(
                {observation_task, stop_task},
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in pending:
                task.cancel()

            if stop_task in done:
                await asyncio.gather(
                    observation_task,
                    return_exceptions=True,
                )
                return

            await asyncio.gather(
                stop_task,
                return_exceptions=True,
            )

            yield observation_task.result()

    async def stop(self) -> None:
        self._stopped = True
        self._stop_event.set()

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
        await self._publish_lifecycle()