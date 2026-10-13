#!/usr/bin/env python3
"""Run repeatable assertions for the isolated terminal capture POC."""

from __future__ import annotations

import argparse
import json
import os
import selectors
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
HELPER = ROOT / "terminal_capture_helper.py"


def collect(
    shell: str,
    command: str,
    *,
    kill_helper: bool = False,
    fail_transport: bool = False,
) -> tuple[list[dict[str, Any]], bytes, bytes, int]:
    with tempfile.TemporaryDirectory(prefix="aegisflow-terminal-poc-") as directory:
        endpoint = Path(directory) / "session.sock"
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(str(endpoint))
        server.listen(1)
        server.settimeout(5)
        command_id = f"cmd-{uuid.uuid4()}"
        helper = subprocess.Popen(
            [
                sys.executable,
                str(HELPER),
                "--endpoint",
                str(endpoint),
                "--command-id",
                command_id,
                "--shell",
                shell,
                command,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        connection, _ = server.accept()
        if fail_transport:
            connection.close()
            return_code = helper.wait(timeout=5)
            server.close()
            stdout, stderr = helper.communicate(timeout=1)
            return [], stdout, stderr, return_code
        connection.settimeout(0.1)
        records: list[dict[str, Any]] = []
        protocol_buffer = b""

        def read_protocol() -> None:
            nonlocal protocol_buffer
            while True:
                try:
                    chunk = connection.recv(4096)
                except socket.timeout:
                    if helper.poll() is not None:
                        return
                    continue
                if not chunk:
                    return
                protocol_buffer += chunk
                while b"\n" in protocol_buffer:
                    line, protocol_buffer = protocol_buffer.split(b"\n", 1)
                    if line:
                        records.append(json.loads(line))

        protocol_thread = threading.Thread(target=read_protocol)
        protocol_thread.start()
        if kill_helper:
            time.sleep(0.1)
            os.kill(helper.pid, signal.SIGTERM)
        return_code = helper.wait(timeout=5)
        protocol_thread.join(timeout=5)
        connection.close()
        server.close()
        stdout, stderr = helper.communicate(timeout=1)
        return records, stdout, stderr, return_code


def assert_normal_capture(shell: str) -> None:
    records, forwarded_stdout, forwarded_stderr, return_code = collect(
        shell,
        "printf 'hello\\n'; printf 'error\\n' >&2",
    )
    outputs = [record for record in records if record["type"] == "terminal.output"]
    assert return_code == 0
    assert forwarded_stdout == b"hello\n"
    assert forwarded_stderr == b"error\n"
    assert {record["stream"] for record in outputs} == {"stdout", "stderr"}
    assert {
        record["stream"]: record["text"]
        for record in outputs
    } == {"stdout": "hello\n", "stderr": "error\n"}
    assert all(record["command_id"] == records[0]["command_id"] for record in records)
    assert records[-1]["type"] == "command.completed"
    assert records[-1]["exit_code"] == 0
    assert all(record["type"] != "command.completed" for record in records[:-1])


def assert_incremental_capture(shell: str) -> None:
    records, forwarded_stdout, _, return_code = collect(
        shell,
        "printf 'one\\n'; sleep 0.2; printf 'two\\n'; sleep 0.2; printf 'three\\n'",
    )
    assert return_code == 0
    assert forwarded_stdout == b"one\ntwo\nthree\n"
    output_indexes = [
        index for index, record in enumerate(records) if record["type"] == "terminal.output"
    ]
    assert len(output_indexes) == 3
    assert output_indexes[-1] < len(records) - 1
    assert [records[index]["text"] for index in output_indexes] == [
        "one\n",
        "two\n",
        "three\n",
    ]


def assert_nonzero_is_not_stderr_failure(shell: str) -> None:
    records, _, forwarded_stderr, return_code = collect(
        shell,
        "printf 'warning\\n' >&2; exit 7",
    )
    assert return_code == 7
    assert forwarded_stderr == b"warning\n"
    assert [record["type"] for record in records] == [
        "command.started",
        "terminal.output",
        "command.completed",
    ]
    assert records[1]["stream"] == "stderr"
    assert records[-1]["exit_code"] == 7


def assert_helper_cleanup(shell: str) -> None:
    records, _, _, return_code = collect(
        shell,
        "sleep 10",
        kill_helper=True,
    )
    assert return_code == 143
    assert records[0]["type"] == "command.started"


def assert_transport_failure_does_not_hang(shell: str) -> None:
    records, forwarded_stdout, _, return_code = collect(
        shell,
        "sleep 0.1; printf 'still-forwarded\\n'",
        fail_transport=True,
    )
    assert records == []
    assert return_code == 0
    assert forwarded_stdout == b"still-forwarded\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--shells", nargs="+", default=["/usr/bin/bash", "/usr/bin/zsh"])
    args = parser.parse_args()

    for shell in args.shells:
        if not Path(shell).exists():
            print(f"SKIP {shell}: unavailable")
            continue
        for _ in range(args.iterations):
            assert_normal_capture(shell)
            assert_incremental_capture(shell)
            assert_nonzero_is_not_stderr_failure(shell)
            assert_transport_failure_does_not_hang(shell)
        assert_helper_cleanup(shell)
        print(f"PASS {shell}: {args.iterations} capture iterations and cleanup")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
