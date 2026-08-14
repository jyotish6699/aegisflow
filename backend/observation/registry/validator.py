from observation.core.provider import ObservationProvider


# =====================================================
# Provider Validation
# =====================================================


def validate_provider(
    provider: object,
) -> None:
    """
    Validate that an object implements the
    Observation Provider contract.

    Raises:
        TypeError: If the object is not a valid
        Observation Provider.
    """

    if not isinstance(provider, ObservationProvider):

        raise TypeError(
            "Provider must implement the "
            "ObservationProvider contract."
        )