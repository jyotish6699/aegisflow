from abc import ABC, abstractmethod

from observation.core.observation import Observation


# =====================================================
# Observation Subscriber
# =====================================================


class ObservationSubscriber(ABC):
    """
    Contract for components that consume Observations.

    Subscribers receive complete Observation objects
    from the Observation Bus.
    """

    @abstractmethod
    async def handle(
        self,
        observation: Observation,
    ) -> None:
        """
        Handle a received Observation.
        """

        raise NotImplementedError