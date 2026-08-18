from collections.abc import AsyncIterator
from pathlib import Path

from observation.core.enums import ProviderType
from observation.core.observation import Observation
from observation.core.provider import ObservationProvider

from .repository import GitRepository


class GitProvider(ObservationProvider):
    """
    Observation Provider for local Git repositories.

    The Git Provider is responsible only for observing the
    Git-specific signals defined by the minimal developer
    workflow prototype.
    """

    def __init__(self, workspace: Path) -> None:
        self._workspace = workspace
        self._repository = GitRepository(workspace)

    @property
    def provider_type(self) -> ProviderType:
        """Return the Git provider identity."""
        return ProviderType.GIT

    async def initialize(self) -> None:
        """
        Prepare the Git Provider.

        Repository detection and Git state initialization
        will be implemented in later steps.
        """

    async def start(self) -> None:
        """
        Activate the Git Provider.

        Continuous observation will be implemented in
        later steps.
        """

    async def observe(self) -> AsyncIterator[Observation]:
        """
        Produce Git observations.

        Git observation generation will be implemented in
        later steps.
        """
        if False:
            yield

    async def stop(self) -> None:
        """
        Stop the Git Provider and release resources.
        """