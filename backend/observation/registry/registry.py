from observation.core.enums import ProviderType
from observation.core.provider import ObservationProvider

from observation.registry.validator import validate_provider


# =====================================================
# Provider Registry
# =====================================================


class ProviderRegistry:
    """
    Maintains registered Observation Providers.

    The registry is responsible only for provider
    registration and lookup.

    It does not start, stop, or execute providers.
    """

    def __init__(self) -> None:

        self._providers: dict[
            ProviderType,
            ObservationProvider,
        ] = {}

    # -------------------------------------------------
    # Register
    # -------------------------------------------------

    def register(
        self,
        provider: ObservationProvider,
    ) -> None:
        """
        Register an Observation Provider.
        """

        validate_provider(provider)

        provider_type = provider.provider_type

        if provider_type in self._providers:

            raise ValueError(
                f"Provider already registered: "
                f"{provider_type.value}"
            )

        self._providers[provider_type] = provider

    # -------------------------------------------------
    # Get
    # -------------------------------------------------

    def get(
        self,
        provider_type: ProviderType,
    ) -> ObservationProvider:
        """
        Return a registered provider.
        """

        try:

            return self._providers[provider_type]

        except KeyError:

            raise KeyError(
                f"Provider not registered: "
                f"{provider_type.value}"
            )

    # -------------------------------------------------
    # List
    # -------------------------------------------------

    def list(
        self,
    ) -> list[ObservationProvider]:
        """
        Return all registered providers.
        """

        return list(
            self._providers.values()
        )

    # -------------------------------------------------
    # Unregister
    # -------------------------------------------------

    def unregister(
        self,
        provider_type: ProviderType,
    ) -> None:
        """
        Remove a registered provider.
        """

        self._providers.pop(
            provider_type,
            None,
        )
