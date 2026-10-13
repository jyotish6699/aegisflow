import asyncio

from observation.dashboard.adapter import DashboardObservationAdapter
from observation.dashboard.state import (
    DashboardState,
    ProviderStatus,
)
from observation.core.enums import ProviderType
from observation.lifecycle.health import ProviderHealth
from observation.logging.runtime import ObservationRuntime


class DashboardRuntimeBridge:
    def __init__(
        self,
        runtime: ObservationRuntime,
        state: DashboardState,
    ) -> None:
        self._runtime = runtime
        self._state = state
        self._adapter = DashboardObservationAdapter(state)
        self._task: asyncio.Task[None] | None = None
        self._lifecycle_task: asyncio.Task[None] | None = None

    @property
    def state(self) -> DashboardState:
        return self._state

    async def consume(self) -> None:
        async for observation in self._runtime.observe():
            self._adapter.apply(observation)

    def _sync_provider_health(
        self,
        health: dict[ProviderType, ProviderHealth],
    ) -> None:
        for provider, lifecycle_state in health.items():
            status = (
                ProviderStatus.RUNNING
                if lifecycle_state == ProviderHealth.RUNNING
                else ProviderStatus.IDLE
            )
            reason = None

            if lifecycle_state == ProviderHealth.FAILED:
                reason = "provider failed"
            elif lifecycle_state in {
                ProviderHealth.STOPPED,
                ProviderHealth.STOPPING,
            }:
                reason = "provider stopped"

            self._state.set_provider_status(
                provider,
                status,
                reason=reason,
            )

    async def _consume_lifecycle(self) -> None:
        async for health in self._runtime.lifecycle_events():
            self._sync_provider_health(health)

    async def start(self) -> None:
        if self._task is not None and not self._task.done():
            return

        await self._runtime.start()
        self._sync_provider_health(
            self._runtime.provider_health()
        )

        self._task = asyncio.create_task(
            self.consume()
        )
        self._lifecycle_task = asyncio.create_task(
            self._consume_lifecycle()
        )

    async def stop(self) -> None:
        await self._runtime.stop()

        if self._task is None:
            return

        await asyncio.gather(
            self._task,
            return_exceptions=True,
        )

        self._task = None

        if self._lifecycle_task is not None:
            self._lifecycle_task.cancel()
            await asyncio.gather(
                self._lifecycle_task,
                return_exceptions=True,
            )
            self._lifecycle_task = None

        self._sync_provider_health(
            self._runtime.provider_health()
        )
        