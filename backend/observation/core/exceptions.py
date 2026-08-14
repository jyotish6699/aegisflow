# =====================================================
# Observation Exceptions
# =====================================================

class ObservationException(Exception):
    """
    Base exception for the Observation Foundation.
    """

    pass


# =====================================================
# Observation Validation
# =====================================================

class InvalidObservationError(ObservationException):
    """
    Raised when an Observation is invalid.
    """

    pass


class InvalidMetadataError(ObservationException):
    """
    Raised when Observation metadata is invalid.
    """

    pass


class InvalidProviderError(ObservationException):
    """
    Raised when an Observation provider is invalid.
    """

    pass