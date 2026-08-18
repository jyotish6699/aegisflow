from collections.abc import AsyncIterator
from pathlib import Path

from observation.core.enums import ProviderType
from observation.core.metadata import ObservationMetadata
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
        self._workspace = workspace.resolve()
        self._repository = GitRepository(self._workspace)

        self._repository_path: Path | None = None
        self._started = False
        self._repository_observation_emitted = False

    @property
    def provider_type(self) -> ProviderType:
        """Return the Git provider identity."""
        return ProviderType.GIT

    async def initialize(self) -> None:
        """
        Discover the Git repository associated with the workspace.
        """
        self._repository_path = self._repository.discover()

    async def start(self) -> None:
        """
        Activate the Git Provider.
        """
        self._started = True

    async def observe(self) -> AsyncIterator[Observation]:
        """
        Produce the repository.detected observation.

        This step implements only repository detection.
        Other Git observations are implemented in later steps.
        """
        if not self._started:
            return

        if self._repository_path is None:
            return

        if self._repository_observation_emitted:
            return

        observation = Observation(
            provider=ProviderType.GIT,
            observation_type="repository.detected",
            metadata=ObservationMetadata(
                source="git",
                attributes={
                    "workspace": str(self._workspace),
                    "repository": str(self._repository_path),
                },
            ),
        )

        self._repository_observation_emitted = True

        yield observation

    async def stop(self) -> None:
        """
        Stop the Git Provider and release provider state.
        """
        self._started = False