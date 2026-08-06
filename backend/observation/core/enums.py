from enum import StrEnum


# =====================================================
# Observation Providers
# =====================================================

class ProviderType(StrEnum):
    """
    Supported Observation Providers.
    """

    GIT = "git"

    TERMINAL = "terminal"

    FILESYSTEM = "filesystem"
