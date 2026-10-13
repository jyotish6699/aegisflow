"""Per-session Unix-domain socket transport for terminal capture events."""

from __future__ import annotations

import json
import socket
import stat
import threading
from asyncio import to_thread
from pathlib import Path

from observation.providers.terminal.capture.protocol import CaptureEvent


class CaptureTransport:
    """Best-effort event sender that isolates transport failure from commands."""

    def __init__(self, endpoint: Path) -> None:
        self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._socket.connect(str(endpoint))
        self._lock = threading.Lock()
        self.failed = False

    def send(self, event: CaptureEvent) -> None:
        payload = (
            json.dumps(event.to_dict(), separators=(",", ":")) + "\n"
        ).encode()
        with self._lock:
            if self.failed:
                return
            try:
                self._socket.sendall(payload)
            except OSError:
                self.failed = True

    def close(self) -> None:
        try:
            self._socket.close()
        except OSError:
            pass


class SessionTransportServer:
    """Own one temporary Unix socket and accept one helper connection."""

    def __init__(self, endpoint: Path) -> None:
        self.endpoint = endpoint
        self._remove_stale_endpoint()
        self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._socket.bind(str(endpoint))
        self._socket.listen(1)
        self._socket.settimeout(5)

    def _remove_stale_endpoint(self) -> None:
        try:
            mode = self.endpoint.stat().st_mode
        except FileNotFoundError:
            return

        if not stat.S_ISSOCK(mode):
            raise FileExistsError(
                f"capture endpoint is not a Unix socket: {self.endpoint}"
            )

        self.endpoint.unlink()

    def accept(self) -> socket.socket | None:
        try:
            connection, _ = self._socket.accept()
        except socket.timeout:
            return None
        return connection

    async def accept_async(self) -> socket.socket | None:
        return await to_thread(self.accept)

    def close(self) -> None:
        self._socket.close()
        try:
            self.endpoint.unlink()
        except FileNotFoundError:
            pass
