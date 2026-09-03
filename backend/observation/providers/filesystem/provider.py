from collections.abc import AsyncIterator
from pathlib import Path

from observation.core.enums import ProviderType
from observation.core.metadata import ObservationMetadata
from observation.core.observation import Observation
from observation.core.provider import ObservationProvider
from observation.providers.filesystem.events import FilesystemEventType

from .watcher import FilesystemWatcher


class FilesystemProvider(ObservationProvider):
    """
    Observation Provider for filesystem activity.

    The Filesystem Provider converts normalized filesystem
    events into canonical AegisFlow Observation objects.
    """

    def __init__(self, workspace: Path) -> None:
        self._workspace = workspace.resolve()

        self._watcher: FilesystemWatcher | None = None

        self._started = False

    @property
    def provider_type(self) -> ProviderType:
        """Return the Filesystem provider identity."""
        return ProviderType.FILESYSTEM

    async def initialize(self) -> None:
        """
        Prepare the Filesystem Provider.

        Observation does not begin during initialization.
        """
        self._watcher = FilesystemWatcher(self._workspace)

    async def start(self) -> None:
        """
        Activate the Filesystem Provider.
        """
        if self._watcher is None:
            return

        self._watcher.start()
        self._started = True

    async def observe(self) -> AsyncIterator[Observation]:
        """
        Consume filesystem events and convert them into
        canonical Observation objects.
        """
        if not self._started:
            return

        if self._watcher is None:
            return

        event = self._watcher.get_event()

        if event is None:
            return

        if event.event_type == FilesystemEventType.CREATED:
            yield Observation(
                provider=ProviderType.FILESYSTEM,
                observation_type="file.created",
                metadata=ObservationMetadata(
                    source="filesystem",
                    attributes={
                        "workspace": str(self._workspace),
                        "path": str(event.path),
                    },
                ),
            )
            return

        if event.event_type == FilesystemEventType.MODIFIED:
            yield Observation(
                provider=ProviderType.FILESYSTEM,
                observation_type="file.modified",
                metadata=ObservationMetadata(
                    source="filesystem",
                    attributes={
                        "workspace": str(self._workspace),
                        "path": str(event.path),
                    },
                ),
            )

        if event.event_type == FilesystemEventType.DELETED:
            yield Observation(
                provider=ProviderType.FILESYSTEM,
                observation_type="file.deleted",
                metadata=ObservationMetadata(
                    source="filesystem",
                    attributes={
                        "workspace": str(self._workspace),
                        "path": str(event.path),
                    },
                ),
            )

    async def stop(self) -> None:
        """
        Stop the Filesystem Provider and release watcher state.
        """
        if self._watcher is not None:
            self._watcher.stop()

        self._watcher = None
        self._started = False