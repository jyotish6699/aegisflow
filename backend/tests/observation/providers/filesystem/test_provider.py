from collections import deque
from pathlib import Path

import asyncio
import pytest

from observation.core.enums import ProviderType
from observation.providers.filesystem.events import (
    FilesystemEvent,
    FilesystemEventType,
)
from observation.providers.filesystem.provider import FilesystemProvider


class FakeFilesystemWatcher:
    def __init__(
        self,
        events: list[FilesystemEvent],
    ) -> None:
        self._events = deque(events)
        self.started = False
        self.stopped = False

    def start(self) -> None:
        self.started = True

    def get_event(self) -> FilesystemEvent | None:
        if not self._events:
            return None

        return self._events.popleft()

    def stop(self) -> None:
        self.stopped = True


@pytest.mark.asyncio
async def test_filesystem_provider_deduplicates_consecutive_modified_events(
    tmp_path: Path,
) -> None:
    """
    FilesystemProvider should emit one file.modified observation
    for consecutive identical modification events for the same path.
    """

    test_file = tmp_path / "test.txt"

    events = [
        FilesystemEvent(
            event_type=FilesystemEventType.MODIFIED,
            path=test_file,
        ),
        FilesystemEvent(
            event_type=FilesystemEventType.MODIFIED,
            path=test_file,
        ),
    ]

    provider = FilesystemProvider(tmp_path)
    provider._watcher = FakeFilesystemWatcher(events)

    await provider.start()

    observations = [
        observation
        async for observation in provider.observe()
    ]

    observations += [
        observation
        async for observation in provider.observe()
    ]

    await provider.stop()

    modified_observations = [
        observation
        for observation in observations
        if observation.observation_type == "file.modified"
    ]

    assert len(modified_observations) == 1


@pytest.mark.asyncio
async def test_filesystem_provider_has_correct_provider_type(
    tmp_path: Path,
) -> None:
    """
    FilesystemProvider should identify itself as the Filesystem provider.
    """

    provider = FilesystemProvider(tmp_path)

    assert provider.provider_type == ProviderType.FILESYSTEM


@pytest.mark.asyncio
async def test_filesystem_provider_does_not_observe_before_start(
    tmp_path: Path,
) -> None:
    """
    FilesystemProvider should not produce observations before start().
    """

    provider = FilesystemProvider(tmp_path)

    await provider.initialize()

    observations = [
        observation
        async for observation in provider.observe()
    ]

    assert observations == []


@pytest.mark.asyncio
async def test_filesystem_provider_stops_observation(
    tmp_path: Path,
) -> None:
    """
    FilesystemProvider should stop producing observations after stop().
    """

    provider = FilesystemProvider(tmp_path)

    await provider.initialize()
    await provider.start()
    await provider.stop()

    observations = [
        observation
        async for observation in provider.observe()
    ]

    assert observations == []


@pytest.mark.asyncio
async def test_filesystem_provider_emits_file_created_observation(
    tmp_path: Path,
) -> None:
    """
    FilesystemProvider should emit a file.created observation
    when a file is created inside the workspace.
    """

    provider = FilesystemProvider(tmp_path)

    await provider.initialize()
    await provider.start()

    test_file = tmp_path / "test.txt"
    test_file.write_text("hello")

    observation = None

    for _ in range(100):
        observations = [
            item
            async for item in provider.observe()
        ]

        if observations:
            observation = observations[0]
            break

        await asyncio.sleep(0.01)

    await provider.stop()

    assert observation is not None
    assert observation.provider == ProviderType.FILESYSTEM
    assert observation.observation_type == "file.created"

    assert observation.metadata.source == "filesystem"

    assert observation.metadata.attributes == {
        "workspace": str(tmp_path),
        "path": str(test_file.resolve()),
    }


@pytest.mark.asyncio
async def test_filesystem_provider_emits_file_modified_observation(
    tmp_path: Path,
) -> None:
    """
    FilesystemProvider should emit a file.modified observation
    when a file is modified inside the workspace.
    """

    test_file = tmp_path / "test.txt"
    test_file.write_text("hello")

    provider = FilesystemProvider(tmp_path)

    await provider.initialize()
    await provider.start()

    test_file.write_text("updated")

    observation = None

    for _ in range(100):
        observations = [
            item
            async for item in provider.observe()
        ]

        for item in observations:
            if item.observation_type == "file.modified":
                observation = item
                break

        if observation is not None:
            break

        await asyncio.sleep(0.01)

    await provider.stop()

    assert observation is not None
    assert observation.provider == ProviderType.FILESYSTEM
    assert observation.observation_type == "file.modified"

    assert observation.metadata.source == "filesystem"

    assert observation.metadata.attributes == {
        "workspace": str(tmp_path),
        "path": str(test_file.resolve()),
    }


@pytest.mark.asyncio
async def test_filesystem_provider_emits_file_deleted_observation(
    tmp_path: Path,
) -> None:
    """
    FilesystemProvider should emit a file.deleted observation
    when a file is deleted inside the workspace.
    """

    test_file = tmp_path / "test.txt"
    test_file.write_text("hello")

    provider = FilesystemProvider(tmp_path)

    await provider.initialize()
    await provider.start()

    test_file.unlink()

    observation = None

    for _ in range(100):
        observations = [
            item
            async for item in provider.observe()
        ]

        for item in observations:
            if item.observation_type == "file.deleted":
                observation = item
                break

        if observation is not None:
            break

        await asyncio.sleep(0.01)

    await provider.stop()

    assert observation is not None
    assert observation.provider == ProviderType.FILESYSTEM
    assert observation.observation_type == "file.deleted"

    assert observation.metadata.source == "filesystem"

    assert observation.metadata.attributes == {
        "workspace": str(tmp_path),
        "path": str(test_file.resolve()),
    }


@pytest.mark.asyncio
async def test_filesystem_provider_ignores_file_outside_workspace(
    tmp_path: Path,
) -> None:
    """
    FilesystemProvider should not emit observations for files
    outside the configured workspace.
    """

    workspace = tmp_path / "workspace"
    outside = tmp_path / "outside"

    workspace.mkdir()
    outside.mkdir()

    provider = FilesystemProvider(workspace)

    await provider.initialize()
    await provider.start()

    outside_file = outside / "outside.txt"
    outside_file.write_text("hello")

    observation = None

    for _ in range(100):
        observations = [
            item
            async for item in provider.observe()
        ]

        if observations:
            observation = observations[0]
            break

        await asyncio.sleep(0.01)

    await provider.stop()

    assert observation is None


@pytest.mark.asyncio
async def test_filesystem_provider_ignores_directory_activity(
    tmp_path: Path,
) -> None:
    """
    FilesystemProvider should not emit observations for
    directory creation inside the workspace.
    """

    provider = FilesystemProvider(tmp_path)

    await provider.initialize()
    await provider.start()

    directory = tmp_path / "subdir"
    directory.mkdir()

    observation = None

    for _ in range(100):
        observations = [
            item
            async for item in provider.observe()
        ]

        if observations:
            observation = observations[0]
            break

        await asyncio.sleep(0.01)

    await provider.stop()

    assert observation is None


@pytest.mark.asyncio
async def test_filesystem_provider_does_not_deduplicate_different_paths(
    tmp_path: Path,
) -> None:
    """
    FilesystemProvider should emit separate file.modified observations
    when consecutive modifications belong to different paths.
    """

    first_file = tmp_path / "first.txt"
    second_file = tmp_path / "second.txt"

    events = [
        FilesystemEvent(
            event_type=FilesystemEventType.MODIFIED,
            path=first_file,
        ),
        FilesystemEvent(
            event_type=FilesystemEventType.MODIFIED,
            path=second_file,
        ),
    ]

    provider = FilesystemProvider(tmp_path)
    provider._watcher = FakeFilesystemWatcher(events)

    await provider.start()

    observations = [
        observation
        async for observation in provider.observe()
    ]

    observations += [
        observation
        async for observation in provider.observe()
    ]

    await provider.stop()

    modified_observations = [
        observation
        for observation in observations
        if observation.observation_type == "file.modified"
    ]

    assert len(modified_observations) == 2

    assert (
        modified_observations[0].metadata.attributes["path"]
        == str(first_file)
    )

    assert (
        modified_observations[1].metadata.attributes["path"]
        == str(second_file)
    )


@pytest.mark.asyncio
async def test_filesystem_provider_resets_deduplication_after_different_event(
    tmp_path: Path,
) -> None:
    """
    FilesystemProvider should emit another file.modified observation
    after a different filesystem event occurs.
    """

    test_file = tmp_path / "test.txt"

    events = [
        FilesystemEvent(
            event_type=FilesystemEventType.MODIFIED,
            path=test_file,
        ),
        FilesystemEvent(
            event_type=FilesystemEventType.CREATED,
            path=test_file,
        ),
        FilesystemEvent(
            event_type=FilesystemEventType.MODIFIED,
            path=test_file,
        ),
    ]

    provider = FilesystemProvider(tmp_path)
    provider._watcher = FakeFilesystemWatcher(events)

    await provider.start()

    observations = []

    for _ in range(3):
        observations += [
            observation
            async for observation in provider.observe()
        ]

    await provider.stop()

    modified_observations = [
        observation
        for observation in observations
        if observation.observation_type == "file.modified"
    ]

    assert len(modified_observations) == 2


@pytest.mark.asyncio
async def test_filesystem_provider_resets_deduplication_on_initialize(
    tmp_path: Path,
) -> None:
    """
    FilesystemProvider should reset modification deduplication state
    when initialized again.
    """

    test_file = tmp_path / "test.txt"

    first_watcher = FakeFilesystemWatcher(
        [
            FilesystemEvent(
                event_type=FilesystemEventType.MODIFIED,
                path=test_file,
            ),
        ]
    )

    provider = FilesystemProvider(tmp_path)
    provider._watcher = first_watcher

    await provider.start()

    first_observations = [
        observation
        async for observation in provider.observe()
    ]

    await provider.stop()

    second_watcher = FakeFilesystemWatcher(
        [
            FilesystemEvent(
                event_type=FilesystemEventType.MODIFIED,
                path=test_file,
            ),
        ]
    )

    await provider.initialize()
    provider._watcher = second_watcher
    await provider.start()

    second_observations = [
        observation
        async for observation in provider.observe()
    ]

    await provider.stop()

    assert len(first_observations) == 1
    assert len(second_observations) == 1

    assert first_observations[0].observation_type == "file.modified"
    assert second_observations[0].observation_type == "file.modified"