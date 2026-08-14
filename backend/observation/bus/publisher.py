from observation.core.observation import Observation

from observation.bus.bus import ObservationBus


# =====================================================
# Observation Publisher
# =====================================================


class ObservationPublisher:
    """
    Publishes complete Observation objects to the
    Observation Bus.

    Providers use the publisher instead of depending
    directly on the internal bus implementation.
    """

    def __init__(
        self,
        bus: ObservationBus,
    ) -> None:

        self._bus = bus

    # -------------------------------------------------
    # Publish
    # -------------------------------------------------

    async def publish(
        self,
        observation: Observation,
    ) -> None:
        """
        Publish an Observation to the Observation Bus.
        """

        await self._bus.publish(
            observation
        )