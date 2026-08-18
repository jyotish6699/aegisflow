from pathlib import Path
import subprocess

from .state import GitState


class GitRepository:
    """
    Provides access to a local Git repository.

    Git-specific interaction is isolated inside this class so
    that GitProvider remains responsible for orchestration and
    observation generation.
    """

    def __init__(self, path: Path) -> None:
        self._path = path.resolve()

    @property
    def path(self) -> Path:
        """Return the configured workspace path."""
        return self._path

    def discover(self) -> Path | None:
        """
        Discover the Git repository containing the configured path.

        Returns:
            The repository root if the path belongs to a Git
            repository, otherwise None.
        """
        try:
            result = subprocess.run(
                [
                    "git",
                    "-C",
                    str(self._path),
                    "rev-parse",
                    "--show-toplevel",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
        except (
            FileNotFoundError,
            subprocess.CalledProcessError,
        ):
            return None

        repository = result.stdout.strip()

        if not repository:
            return None

        return Path(repository).resolve()

    def get_state(self) -> GitState:
        """
        Return the current Git repository state.

        Git state reading will be implemented in later steps.
        """
        raise NotImplementedError