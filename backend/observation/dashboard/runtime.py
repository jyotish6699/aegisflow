import asyncio

from observation.dashboard.adapter import DashboardObservationAdapter
from observation.dashboard.state import DashboardState
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

    @property
    def state(self) -> DashboardState:
        return self._state

    async def consume(self) -> None:
        async for observation in self._runtime.observe():
            self._adapter.apply(observation)

    async def start(self) -> None:
        if self._task is not None and not self._task.done():
            return

        self._task = asyncio.create_task(
            self.consume()
        )

    async def stop(self) -> None:
        if self._task is None:
            return

        self._task.cancel()

        await asyncio.gather(
            self._task,
            return_exceptions=True,
        )

        self._task = None
        