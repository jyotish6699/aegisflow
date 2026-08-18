from pathlib import Path

from .state import GitState


class GitRepository:
    """
    Provides access to a local Git repository.

    Git-specific interaction is isolated inside this class so
    that GitProvider remains responsible for orchestration and
    observation generation.
    """

    def __init__(self, path: Path) -> None:
        self._path = path

    @property
    def path(self) -> Path:
        """Return the configured repository path."""
        return self._path

    def get_state(self) -> GitState:
        """
        Return the current Git repository state.

        Git state reading will be implemented in a later step.
        """
        raise NotImplementedError