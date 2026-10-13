import json
import os
import signal
import socket
import subprocess
import sys
import threading
import time
import tempfile
import uuid
from pathlib import Path
from typing import Any

import pytest

from observation.providers.terminal.capture.transport import (
    SessionTransportServer,
)
from observation.providers.terminal.capture.helper import CommandCapture


BACKEND = Path(__file__).parents[4]
HELPER_MODULE = "observation.providers.terminal.capture.helper"


def available_shells() -> list[str]:
    return [
        shell
        for shell in ("/usr/bin/bash", "/usr/bin/zsh")
        if Path(shell).exists()
    ]


def test_command_capture_rejects_empty_shell() -> None:
    with pytest.raises(
        ValueError,
        match="shell executable must be non-empty",
    ):
        CommandCapture(
            endpoint=Path("/tmp/unused.sock"),
            shell="",
            command="true",
            cwd=Path.cwd(),
            session_id="session",
            command_id="command",
        )


def test_command_capture_rejects_unknown_shell() -> None:
    with pytest.raises(
        ValueError,
        match="shell executable not found",
    ):
        CommandCapture(
            endpoint=Path("/tmp/unused.sock"),
            shell="definitely-not-a-shell",
            command="true",
            cwd=Path.cwd(),
            session_id="session",
            command_id="command",
        )


def test_transport_replaces_stale_socket_endpoint(
    tmp_path: Path,
) -> None:
    endpoint = tmp_path / "capture.sock"
    stale_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    stale_socket.bind(str(endpoint))
    stale_socket.close()

    second_server = SessionTransportServer(endpoint)
    second_server.close()

    assert not endpoint.exists()


def run_capture(
    tmp_path: Path,
    shell: str,
    command: str,
    *,
    disconnect: bool = False,
    terminate: bool = False,
) -> tuple[list[dict[str, Any]], bytes, bytes, int, list[float]]:
    endpoint = Path(tempfile.gettempdir()) / f"af-{uuid.uuid4()}.sock"
    server = SessionTransportServer(endpoint)
    session_id = f"session-{uuid.uuid4()}"
    command_id = f"command-{uuid.uuid4()}"
    helper = subprocess.Popen(
        [
            sys.executable,
            "-m",
            HELPER_MODULE,
            "--endpoint",
            str(endpoint),
            "--session-id",
            session_id,
            "--command-id",
            command_id,
            "--shell",
            shell,
            command,
        ],
        cwd=BACKEND,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    connection = server.accept()
    arrivals: list[float] = []
    records: list[dict[str, Any]] = []
    buffer = b""

    def read_records() -> None:
        nonlocal buffer
        while True:
            try:
                chunk = connection.recv(4096)
            except OSError:
                return
            if not chunk:
                return
            buffer += chunk
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                if line:
                    records.append(json.loads(line))
                    arrivals.append(time.monotonic())

    reader = threading.Thread(target=read_records)
    reader.start()
    if disconnect:
        connection.shutdown(socket.SHUT_RDWR)
    if terminate:
        time.sleep(0.1)
        os.kill(helper.pid, signal.SIGTERM)

    return_code = helper.wait(timeout=5)
    reader.join(timeout=5)
    connection.close()
    server.close()
    stdout, stderr = helper.communicate(timeout=1)
    return records, stdout, stderr, return_code, arrivals


@pytest.mark.parametrize("shell", available_shells())
def test_capture_preserves_streams_and_identity(
    tmp_path: Path,
    shell: str,
) -> None:
    records, stdout, stderr, return_code, _ = run_capture(
        tmp_path,
        shell,
        "printf 'hello\\n'; printf 'error\\n' >&2",
    )

    assert return_code == 0
    assert stdout == b"hello\n"
    assert stderr == b"error\n"
    assert {record["type"] for record in records} == {
        "command.started",
        "terminal.output",
        "command.completed",
    }
    assert all(record["version"] == 1 for record in records)
    assert len({record["session_id"] for record in records}) == 1
    assert len({record["command_id"] for record in records}) == 1
    assert [record["sequence"] for record in records] == list(
        range(1, len(records) + 1)
    )
    assert [
        record["stream"]
        for record in records
        if record["type"] == "terminal.output"
    ] == ["stdout", "stderr"] or [
        record["stream"]
        for record in records
        if record["type"] == "terminal.output"
    ] == ["stderr", "stdout"]


@pytest.mark.parametrize("shell", available_shells())
def test_capture_is_incremental_and_completes_after_drain(
    tmp_path: Path,
    shell: str,
) -> None:
    records, stdout, _, return_code, arrivals = run_capture(
        tmp_path,
        shell,
        "printf 'one\\n'; sleep 0.2; printf 'two\\n'; sleep 0.2; printf 'three\\n'",
    )

    output_indexes = [
        index for index, record in enumerate(records)
        if record["type"] == "terminal.output"
    ]
    completion_index = next(
        index
        for index, record in enumerate(records)
        if record["type"] == "command.completed"
    )
    assert return_code == 0
    assert stdout == b"one\ntwo\nthree\n"
    assert len(output_indexes) >= 2
    assert output_indexes[-1] < completion_index
    assert arrivals[output_indexes[0]] < arrivals[completion_index]
    assert [
        records[index]["text"] for index in output_indexes
    ] == ["one\n", "two\n", "three\n"]


@pytest.mark.parametrize("shell", available_shells())
def test_capture_reports_nonzero_exit_without_classifying_stderr_as_failure(
    tmp_path: Path,
    shell: str,
) -> None:
    records, _, stderr, return_code, _ = run_capture(
        tmp_path,
        shell,
        "printf 'warning\\n' >&2; exit 7",
    )

    assert return_code == 7
    assert stderr == b"warning\n"
    assert records[-1]["type"] == "command.completed"
    assert records[-1]["exit_code"] == 7
    assert records[-2]["type"] == "terminal.output"
    assert records[-2]["stream"] == "stderr"


@pytest.mark.parametrize("shell", available_shells())
def test_capture_transport_disconnect_does_not_hang_command(
    tmp_path: Path,
    shell: str,
) -> None:
    records, stdout, _, return_code, _ = run_capture(
        tmp_path,
        shell,
        "sleep 0.1; printf 'forwarded\\n'",
        disconnect=True,
    )

    assert all(record["type"] != "terminal.output" for record in records)
    assert stdout == b"forwarded\n"
    assert return_code == 0


@pytest.mark.parametrize("shell", available_shells())
def test_capture_termination_cleans_up_child_process(
    tmp_path: Path,
    shell: str,
) -> None:
    records, _, _, return_code, _ = run_capture(
        tmp_path,
        shell,
        "sleep 10",
        terminate=True,
    )

    assert records[0]["type"] == "command.started"
    assert return_code == 143
