from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GitState:
    """
    Represents the Git state observed by the Git Provider.

    The state contains only information required by the
    minimal Git observation prototype.
    """

    repository: Path
    branch: str | None
    head: str | None
    working_tree_status: str