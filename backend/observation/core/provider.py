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

    A provider is responsible for observing one external
    system and producing canonical Observation objects.

    Providers must not interpret observations or generate
    business events directly.
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
        Prepare the provider for execution.
        """
        raise NotImplementedError

    @abstractmethod
    async def start(self) -> None:
        """
        Start provider activity.
        """
        raise NotImplementedError

    @abstractmethod
    async def observe(self) -> AsyncIterator[Observation]:
        """
        Produce observations detected by the provider.
        """
        raise NotImplementedError

    @abstractmethod
    async def stop(self) -> None:
        """
        Stop provider activity and release resources.
        """
        raise NotImplementedError