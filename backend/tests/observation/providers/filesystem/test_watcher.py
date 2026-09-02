import time
from pathlib import Path


from observation.providers.filesystem.events import (
    FilesystemEvent,
    FilesystemEventType,
)
from observation.providers.filesystem.watcher import (
    FilesystemWatcher,
)


def wait_for_event(
    watcher: FilesystemWatcher,
    event_type: FilesystemEventType,
    timeout: float = 1.0,
) -> FilesystemEvent | None:
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        event = watcher.get_event()

        if event is not None and event.event_type == event_type:
            return event

        time.sleep(0.01)

    return None


def test_filesystem_watcher_starts_and_stops(
    tmp_path: Path,
) -> None:
    """
    FilesystemWatcher should start and stop without errors.
    """

    watcher = FilesystemWatcher(tmp_path)

    watcher.start()
    watcher.stop()


def test_filesystem_watcher_can_restart(
    tmp_path: Path,
) -> None:
    """
    FilesystemWatcher should be able to start again after stop().
    """

    watcher = FilesystemWatcher(tmp_path)

    watcher.start()
    watcher.stop()

    watcher.start()

    test_file = tmp_path / "test.txt"
    test_file.write_text("hello")

    event = wait_for_event(
        watcher,
        FilesystemEventType.CREATED,
    )

    watcher.stop()

    assert event is not None
    assert event.path == test_file.resolve()


def test_filesystem_watcher_detects_created_file(
    tmp_path: Path,
) -> None:
    """
    FilesystemWatcher should emit a created event for a file.
    """

    watcher = FilesystemWatcher(tmp_path)
    watcher.start()

    test_file = tmp_path / "test.txt"
    test_file.write_text("hello")

    event = wait_for_event(
        watcher,
        FilesystemEventType.CREATED,
    )

    watcher.stop()

    assert event is not None
    assert event.path == test_file.resolve()


def test_filesystem_watcher_detects_modified_file(
    tmp_path: Path,
) -> None:
    """
    FilesystemWatcher should emit a modified event for a file.
    """

    test_file = tmp_path / "test.txt"
    test_file.write_text("hello")

    watcher = FilesystemWatcher(tmp_path)
    watcher.start()

    test_file.write_text("updated")

    event = wait_for_event(
        watcher,
        FilesystemEventType.MODIFIED,
    )

    watcher.stop()

    assert event is not None
    assert event.path == test_file.resolve()


def test_filesystem_watcher_detects_deleted_file(
    tmp_path: Path,
) -> None:
    """
    FilesystemWatcher should emit a deleted event for a file.
    """

    test_file = tmp_path / "test.txt"
    test_file.write_text("hello")

    watcher = FilesystemWatcher(tmp_path)
    watcher.start()

    test_file.unlink()

    event = wait_for_event(
        watcher,
        FilesystemEventType.DELETED,
    )

    watcher.stop()

    assert event is not None
    assert event.path == test_file.resolve()


def test_filesystem_watcher_ignores_directory_events(
    tmp_path: Path,
) -> None:
    """
    FilesystemWatcher should not emit events for directories.
    """

    watcher = FilesystemWatcher(tmp_path)
    watcher.start()

    (tmp_path / "subdir").mkdir()

    time.sleep(0.1)

    event = watcher.get_event()

    watcher.stop()

    assert event is None
