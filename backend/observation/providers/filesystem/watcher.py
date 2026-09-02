from pathlib import Path
from queue import Empty, Queue

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from .events import FilesystemEvent, FilesystemEventType


class FilesystemEventHandlerAdapter(FileSystemEventHandler):
    """
    Converts Watchdog filesystem events into internal
    FilesystemEvent objects.
    """

    def __init__(self, event_queue: Queue[FilesystemEvent]) -> None:
        self._event_queue = event_queue

    def on_created(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return

        self._event_queue.put(
            FilesystemEvent(
                event_type=FilesystemEventType.CREATED,
                path=Path(event.src_path).resolve(),
            )
        )

    def on_modified(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return

        self._event_queue.put(
            FilesystemEvent(
                event_type=FilesystemEventType.MODIFIED,
                path=Path(event.src_path).resolve(),
            )
        )

    def on_deleted(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return

        self._event_queue.put(
            FilesystemEvent(
                event_type=FilesystemEventType.DELETED,
                path=Path(event.src_path).resolve(),
            )
        )


class FilesystemWatcher:
    """
    Watches a workspace using Watchdog and exposes normalized
    filesystem events through a queue.
    """

    def __init__(self, workspace: Path) -> None:
        self._workspace = workspace.resolve()
        self._event_queue: Queue[FilesystemEvent] = Queue()

        self._observer: Observer | None = None
        self._handler = FilesystemEventHandlerAdapter(self._event_queue)

        self._started = False

    def start(self) -> None:
        if self._started:
            return

        self._observer = Observer()

        self._observer.schedule(
            self._handler,
            str(self._workspace),
            recursive=True,
        )
        self._observer.start()

        self._started = True

    def get_event(self) -> FilesystemEvent | None:
        try:
            return self._event_queue.get_nowait()
        except Empty:
            return None

    def stop(self) -> None:
        if not self._started:
            return

        if self._observer is not None:
            self._observer.stop()
            self._observer.join()
            self._observer = None

        self._started = False
