from collections.abc import Iterable

from observation.core.provider import ObservationProvider
from observation.lifecycle.health import (
    ProviderHealth,
    ProviderHealthTracker,
)


# =====================================================
# Observation Provider Starter
# =====================================================


class ProviderStarter:
    """
    Initializes and starts Observation Providers.

    The starter manages provider startup only.
    Provider discovery and loading are handled by the
    Registry and ProviderLoader respectively.
    """

    def __init__(
        self,
        health: ProviderHealthTracker,
    ) -> None:

        self._health = health

    # -------------------------------------------------
    # Start Provider
    # -------------------------------------------------

    async def start(
        self,
        provider: ObservationProvider,
    ) -> bool:
        """
        Initialize and start a single provider.

        Returns True when the provider starts
        successfully and False when startup fails.
        """

        provider_type = provider.provider_type

        try:

            self._health.set_state(
                provider_type,
                ProviderHealth.INITIALIZING,
            )

            await provider.initialize()

            self._health.set_state(
                provider_type,
                ProviderHealth.READY,
            )

            await provider.start()

            self._health.set_state(
                provider_type,
                ProviderHealth.RUNNING,
            )

            return True

        except Exception:

            self._health.set_state(
                provider_type,
                ProviderHealth.FAILED,
            )

            return False

    # -------------------------------------------------
    # Start Providers
    # -------------------------------------------------

    async def start_all(
        self,
        providers: Iterable[ObservationProvider],
    ) -> list[ObservationProvider]:
        """
        Initialize and start all supplied providers.

        Providers are started independently. A failure in
        one provider does not prevent other providers from
        starting.

        Returns the providers that started successfully.
        """

        started: list[
            ObservationProvider
        ] = []

        for provider in providers:

            success = await self.start(
                provider
            )

            if success:

                started.append(provider)

        return started