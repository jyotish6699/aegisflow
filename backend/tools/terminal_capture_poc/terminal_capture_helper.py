#!/usr/bin/env python3
"""Isolated command-capture proof of concept.

This helper is deliberately outside the observation provider implementation.
It runs one explicitly supplied command, forwards stdout/stderr unchanged,
and sends JSONL records to a per-session Unix-domain socket.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import threading
import uuid
from pathlib import Path
from typing import BinaryIO


class CaptureTransport:
    def __init__(self, endpoint: Path) -> None:
        self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._socket.connect(str(endpoint))
        self._lock = threading.Lock()
        self.failed = False

    def send(self, record: dict[str, object]) -> None:
        payload = (json.dumps(record, separators=(",", ":")) + "\n").encode()
        with self._lock:
            if self.failed:
                return
            try:
                self._socket.sendall(payload)
            except OSError:
                self.failed = True

    def close(self) -> None:
        self._socket.close()


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


def run(args: argparse.Namespace) -> int:
    transport = CaptureTransport(Path(args.endpoint))
    command_id = args.command_id or str(uuid.uuid4())
    sequence = 0
    process: subprocess.Popen[bytes] | None = None

    def send(record_type: str, **fields: object) -> None:
        nonlocal sequence
        sequence += 1
        transport.send(
            {
                "type": record_type,
                "command_id": command_id,
                "sequence": sequence,
                **fields,
            }
        )

    def stop_child(_signum: int, _frame: object) -> None:
        if process is not None:
            _terminate_process_group(process)
        transport.close()
        raise SystemExit(143)

    signal.signal(signal.SIGTERM, stop_child)
    signal.signal(signal.SIGINT, stop_child)

    send("command.started", command=args.command, shell=args.shell)
    process = subprocess.Popen(
        [args.shell, "-c", args.command],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )

    def drain(stream: BinaryIO, output: BinaryIO, stream_name: str) -> None:
        while True:
            chunk = os.read(stream.fileno(), 4096)
            if not chunk:
                return
            output.write(chunk)
            output.flush()
            send("terminal.output", stream=stream_name, text=chunk.decode(errors="replace"))

    assert process.stdout is not None
    assert process.stderr is not None
    stdout_thread = threading.Thread(
        target=drain,
        args=(process.stdout, sys.stdout.buffer, "stdout"),
        daemon=False,
    )
    stderr_thread = threading.Thread(
        target=drain,
        args=(process.stderr, sys.stderr.buffer, "stderr"),
        daemon=False,
    )
    stdout_thread.start()
    stderr_thread.start()
    exit_code = process.wait()
    stdout_thread.join()
    stderr_thread.join()

    send("command.completed", exit_code=exit_code)
    transport.close()
    return exit_code


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--command-id")
    parser.add_argument("--shell", required=True)
    parser.add_argument("command")
    return run(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
