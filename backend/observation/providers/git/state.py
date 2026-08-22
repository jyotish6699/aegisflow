from pathlib import Path
import subprocess

from pydantic import BaseModel

from .exceptions import GitStateUnavailableError


# =====================================================
# Git State
# =====================================================


class GitState(BaseModel):
    """
    Snapshot of the current state of a Git repository.

    GitState only represents current repository state.
    It does not detect changes or create observations.
    """

    branch: str

    working_tree_clean: bool

    commit: str

    @classmethod
    def read(cls, repository: Path) -> "GitState":
        """
        Read the current state of a Git repository.
        """

        branch = subprocess.run(
            ["git", "-C", str(repository), "branch", "--show-current"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

        status = subprocess.run(
            ["git", "-C", str(repository), "status", "--porcelain"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout

        try:
            commit = subprocess.run(
                ["git", "-C", str(repository), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        except subprocess.CalledProcessError as exc:
            raise GitStateUnavailableError(
                "Git repository does not have an initial commit."
            ) from exc

        return cls(
            branch=branch,
            working_tree_clean=not bool(status.strip()),
            commit=commit,
        )