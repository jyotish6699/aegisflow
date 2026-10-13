"""Command helper for the production terminal capture transport."""

from __future__ import annotations

import argparse
import os
import signal
import shutil
import subprocess
import sys
import threading
import uuid
from pathlib import Path
from typing import BinaryIO

from observation.providers.terminal.capture.protocol import CaptureEvent
from observation.providers.terminal.capture.transport import CaptureTransport


def _terminate_process_group(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


class CommandCapture:
    """Run one explicitly selected shell command through a session transport."""

    def __init__(
        self,
        *,
        endpoint: Path,
        shell: str,
        command: str,
        cwd: Path | None,
        session_id: str,
        command_id: str,
    ) -> None:
        self._shell_executable = self._resolve_shell(shell)
        self._shell = Path(self._shell_executable).name
        self._transport = CaptureTransport(endpoint)
        self._command = command
        self._cwd = cwd
        self._event_cwd = str(cwd or Path.cwd())
        self._session_id = session_id
        self._command_id = command_id
        self._sequence = 0
        self._process: subprocess.Popen[bytes] | None = None

    @staticmethod
    def _resolve_shell(shell: str) -> str:
        if not shell:
            raise ValueError("shell executable must be non-empty")

        executable = shutil.which(shell)
        if executable is None:
            raise ValueError(
                f"shell executable not found: {shell!r}"
            )
        return executable

    def _send(self, event_type: str, **fields: object) -> None:
        self._sequence += 1
        fields.setdefault("cwd", self._event_cwd)
        self._transport.send(
            CaptureEvent.create(
                session_id=self._session_id,
                command_id=self._command_id,
                sequence=self._sequence,
                event_type=event_type,
                **fields,
            )
        )

    def _handle_signal(self, _signum: int, _frame: object) -> None:
        if self._process is not None:
            _terminate_process_group(self._process)
        self._transport.close()
        raise SystemExit(143)

    def run(self) -> int:
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
        self._send(
            "command.started",
            command=self._command,
            shell=self._shell,
        )
        self._process = subprocess.Popen(
            [self._shell_executable, "-c", self._command],
            cwd=self._cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )

        def drain(
            stream: BinaryIO,
            output: BinaryIO,
            stream_name: str,
        ) -> None:
            while True:
                chunk = os.read(stream.fileno(), 4096)
                if not chunk:
                    return
                output.write(chunk)
                output.flush()
                self._send(
                    "terminal.output",
                    stream=stream_name,
                    text=chunk.decode(errors="replace"),
                )

        assert self._process.stdout is not None
        assert self._process.stderr is not None
        stdout_thread = threading.Thread(
            target=drain,
            args=(self._process.stdout, sys.stdout.buffer, "stdout"),
        )
        stderr_thread = threading.Thread(
            target=drain,
            args=(self._process.stderr, sys.stderr.buffer, "stderr"),
        )
        stdout_thread.start()
        stderr_thread.start()
        exit_code = self._process.wait()
        stdout_thread.join()
        stderr_thread.join()
        self._send("command.completed", exit_code=exit_code)
        self._transport.close()
        return exit_code


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", required=True, type=Path)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--command-id", required=True)
    parser.add_argument("--shell", required=True)
    parser.add_argument("--cwd", type=Path)
    parser.add_argument("command")
    args = parser.parse_args()
    return CommandCapture(
        endpoint=args.endpoint,
        shell=args.shell,
        command=args.command,
        cwd=args.cwd,
        session_id=args.session_id,
        command_id=args.command_id,
    ).run()


if __name__ == "__main__":
    raise SystemExit(main())
