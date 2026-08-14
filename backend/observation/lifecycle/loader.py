from observation.config.settings import ObservationSettings
from observation.core.provider import ObservationProvider
from observation.registry.registry import ProviderRegistry


# =====================================================
# Observation Provider Loader
# =====================================================


class ProviderLoader:
    """
    Loads the Observation Providers enabled by configuration.

    The loader selects providers from the registry based
    on the configured provider types.

    It does not initialize or start providers.
    """

    def __init__(
        self,
        registry: ProviderRegistry,
        settings: ObservationSettings,
    ) -> None:

        self._registry = registry
        self._settings = settings

    # -------------------------------------------------
    # Load Providers
    # -------------------------------------------------

    def load(
        self,
    ) -> list[ObservationProvider]:
        """
        Return the providers enabled by configuration
        and available in the registry.
        """

        if not self._settings.enabled:

            return []

        providers: list[
            ObservationProvider
        ] = []

        for provider_type in self._settings.providers:

            provider = self._registry.get(
                provider_type
            )

            providers.append(provider)

        return providers