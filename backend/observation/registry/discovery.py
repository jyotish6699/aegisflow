from collections.abc import Iterable

from observation.core.provider import ObservationProvider


# =====================================================
# Provider Discovery
# =====================================================


def discover_providers(
    providers: Iterable[type[ObservationProvider]],
) -> list[type[ObservationProvider]]:
    """
    Discover available Observation Provider classes.

    Phase 1 uses explicit provider registration.

    Dynamic plugin discovery will be introduced when
    the provider/plugin system is implemented.
    """

    return list(providers)
