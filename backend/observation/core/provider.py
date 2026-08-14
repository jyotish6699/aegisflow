from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from observation.core.enums import ProviderType
from observation.core.observation import Observation


# =====================================================
# Observation Provider
# =====================================================


class ObservationProvider(ABC):
    """
    Base contract for every AegisFlow Observation Provider.

    A provider observes one external system and produces
    canonical Observation objects.

    Providers must not interpret observations or generate
    business events directly.

    Provider lifecycle:

        initialize()
            ↓
        start()
            ↓
        observe()
            ↓
        stop()
    """

    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """
        Return the provider's identity.
        """
        raise NotImplementedError

    @abstractmethod
    async def initialize(self) -> None:
        """
        Prepare resources required by the provider.

        This method should not begin continuous observation.
        """
        raise NotImplementedError

    @abstractmethod
    async def start(self) -> None:
        """
        Activate the provider.

        This method prepares the provider to begin
        producing observations.
        """
        raise NotImplementedError

    @abstractmethod
    async def observe(self) -> AsyncIterator[Observation]:
        """
        Produce observations as an asynchronous stream.

        Each yielded item must be a complete Observation
        object.
        """
        raise NotImplementedError

    @abstractmethod
    async def stop(self) -> None:
        """
        Stop observation and release provider resources.
        """
        raise NotImplementedError