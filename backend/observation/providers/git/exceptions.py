# =====================================================
# Git Provider Exceptions
# =====================================================


class GitProviderError(Exception):
    """
    Base exception for Git Provider errors.
    """

    pass


class GitStateUnavailableError(GitProviderError):
    """
    Raised when Git repository state is temporarily unavailable.

    This currently represents an unborn Git repository where
    HEAD does not exist because no commit has been created yet.
    """

    pass