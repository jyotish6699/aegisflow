from observation.core.observation import Observation

from observation.bus.subscriber import ObservationSubscriber


# =====================================================
# Observation Bus
# =====================================================


class ObservationBus:
    """
    In-process asynchronous bus for Observation objects.

    The bus transports complete Observation objects
    from publishers to registered subscribers.

    It does not interpret, transform, or persist
    observations.
    """

    def __init__(self) -> None:

        self._subscribers: list[
            ObservationSubscriber
        ] = []

    # -------------------------------------------------
    # Subscribe
    # -------------------------------------------------

    def subscribe(
        self,
        subscriber: ObservationSubscriber,
    ) -> None:
        """
        Register an Observation subscriber.
        """

        if subscriber not in self._subscribers:

            self._subscribers.append(
                subscriber
            )

    # -------------------------------------------------
    # Unsubscribe
    # -------------------------------------------------

    def unsubscribe(
        self,
        subscriber: ObservationSubscriber,
    ) -> None:
        """
        Remove an Observation subscriber.
        """

        if subscriber in self._subscribers:

            self._subscribers.remove(
                subscriber
            )

    # -------------------------------------------------
    # Publish
    # -------------------------------------------------

    async def publish(
        self,
        observation: Observation,
    ) -> None:
        """
        Deliver an Observation to all registered
        subscribers.
        """

        for subscriber in self._subscribers:

            await subscriber.handle(
                observation
            )