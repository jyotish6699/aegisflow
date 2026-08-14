from collections.abc import Iterable

from observation.core.provider import ObservationProvider
from observation.lifecycle.health import (
    ProviderHealth,
    ProviderHealthTracker,
)


# =====================================================
# Observation Provider Stopper
# =====================================================


class ProviderStopper:
    """
    Stops Observation Providers and updates their
    lifecycle health state.

    The stopper manages provider shutdown only.
    """

    def __init__(
        self,
        health: ProviderHealthTracker,
    ) -> None:

        self._health = health

    # -------------------------------------------------
    # Stop Provider
    # -------------------------------------------------

    async def stop(
        self,
        provider: ObservationProvider,
    ) -> bool:
        """
        Stop a single Observation Provider.

        Returns True when the provider stops
        successfully and False when shutdown fails.
        """

        provider_type = provider.provider_type

        try:

            self._health.set_state(
                provider_type,
                ProviderHealth.STOPPING,
            )

            await provider.stop()

            self._health.set_state(
                provider_type,
                ProviderHealth.STOPPED,
            )

            return True

        except Exception:

            self._health.set_state(
                provider_type,
                ProviderHealth.FAILED,
            )

            return False

    # -------------------------------------------------
    # Stop Providers
    # -------------------------------------------------

    async def stop_all(
        self,
        providers: Iterable[ObservationProvider],
    ) -> list[ObservationProvider]:
        """
        Stop all supplied providers.

        Providers are stopped independently. A failure in
        one provider does not prevent other providers from
        being stopped.

        Returns the providers that stopped successfully.
        """

        stopped: list[
            ObservationProvider
        ] = []

        for provider in providers:

            success = await self.stop(
                provider
            )

            if success:

                stopped.append(provider)

        return stopped