from collections.abc import AsyncIterator
from pathlib import Path

from observation.core.enums import ProviderType
from observation.core.metadata import ObservationMetadata
from observation.core.observation import Observation
from observation.core.provider import ObservationProvider

from .exceptions import GitStateUnavailableError
from .repository import GitRepository
from .state import GitState


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
        self._state: GitState | None = None

        self._started = False
        self._repository_observation_emitted = False

    @property
    def provider_type(self) -> ProviderType:
        """Return the Git provider identity."""
        return ProviderType.GIT

    async def initialize(self) -> None:
        """
        Discover the Git repository associated with the workspace
        and establish its initial Git state when available.
        """
        self._repository_path = self._repository.discover()

        if self._repository_path is None:
            self._state = None
            return

        try:
            self._state = GitState.read(self._repository_path)
        except GitStateUnavailableError:
            self._state = None

    async def start(self) -> None:
        """
        Activate the Git Provider.
        """
        self._started = True

    async def observe(self) -> AsyncIterator[Observation]:
        """
        Produce Git observations defined by the minimal
        developer workflow prototype.

        The provider emits repository.detected once and
        subsequently checks for Git state changes.
        """
        if not self._started:
            return

        if self._repository_path is None:
            return

        # -------------------------------------------------
        # Repository Detection
        # -------------------------------------------------

        if not self._repository_observation_emitted:
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
            return

        # -------------------------------------------------
        # Branch Change Detection
        # -------------------------------------------------

        try:
            current_state = GitState.read(self._repository_path)
        except GitStateUnavailableError:
            self._state = None
            return

        if self._state is None:
            self._state = current_state
            return

        if current_state.branch != self._state.branch:
            observation = Observation(
                provider=ProviderType.GIT,
                observation_type="branch.changed",
                metadata=ObservationMetadata(
                    source="git",
                    attributes={
                        "workspace": str(self._workspace),
                        "repository": str(self._repository_path),
                        "branch": current_state.branch,
                    },
                ),
            )

            self._state = self._state.model_copy(
                update={
                    "branch": current_state.branch,
                }
            )

            yield observation
            return

        if current_state.working_tree_clean != self._state.working_tree_clean:
            observation = Observation(
                provider=ProviderType.GIT,
                observation_type="working_tree.changed",
                metadata=ObservationMetadata(
                    source="git",
                    attributes={
                        "workspace": str(self._workspace),
                        "repository": str(self._repository_path),
                        "working_tree_clean": current_state.working_tree_clean,
                    },
                ),
            )

            self._state = self._state.model_copy(
                update={
                    "working_tree_clean": current_state.working_tree_clean,
                }
            )

            yield observation
            return

        if current_state.commit != self._state.commit:
            observation = Observation(
                provider=ProviderType.GIT,
                observation_type="commit.changed",
                metadata=ObservationMetadata(
                    source="git",
                    attributes={
                        "workspace": str(self._workspace),
                        "repository": str(self._repository_path),
                        "commit": current_state.commit,
                        "commit_message": current_state.commit_message,
                    },
                ),
            )

            self._state = current_state

            yield observation
            return

        self._state = current_state

    async def stop(self) -> None:
        """
        Stop the Git Provider and release provider state.
        """
        self._started = False
        self._state = None