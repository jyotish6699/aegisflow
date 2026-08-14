from enum import StrEnum

from observation.core.enums import ProviderType


# =====================================================
# Provider Health State
# =====================================================


class ProviderHealth(StrEnum):
    """
    Runtime health state of an Observation Provider.
    """

    CREATED = "created"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


# =====================================================
# Provider Health Tracker
# =====================================================


class ProviderHealthTracker:
    """
    Tracks runtime health for Observation Providers.

    The tracker only records provider state.
    It does not start, stop, or restart providers.
    """

    def __init__(self) -> None:

        self._states: dict[
            ProviderType,
            ProviderHealth,
        ] = {}

    # -------------------------------------------------
    # Set State
    # -------------------------------------------------

    def set_state(
        self,
        provider_type: ProviderType,
        state: ProviderHealth,
    ) -> None:
        """
        Set the current health state of a provider.
        """

        self._states[provider_type] = state

    # -------------------------------------------------
    # Get State
    # -------------------------------------------------

    def get_state(
        self,
        provider_type: ProviderType,
    ) -> ProviderHealth | None:
        """
        Return the current state of a provider.

        Returns None when the provider has not yet been
        tracked.
        """

        return self._states.get(
            provider_type
        )

    # -------------------------------------------------
    # Snapshot
    # -------------------------------------------------

    def snapshot(
        self,
    ) -> dict[ProviderType, ProviderHealth]:
        """
        Return a snapshot of all tracked provider states.
        """

        return self._states.copy()