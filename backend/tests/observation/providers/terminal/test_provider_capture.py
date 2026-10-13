import asyncio
import json
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

import pytest

from observation.core.enums import ProviderType
from observation.providers.terminal.provider import TerminalProvider


BACKEND = Path(__file__).parents[4]
HELPER_MODULE = "observation.providers.terminal.capture.helper"


def start_helper(
    endpoint: Path,
    workspace: Path,
    command: str,
    shell: str = "/usr/bin/bash",
) -> subprocess.Popen[bytes]:
    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            HELPER_MODULE,
            "--endpoint",
            str(endpoint),
            "--session-id",
            f"session-{uuid.uuid4()}",
            "--command-id",
            f"command-{uuid.uuid4()}",
            "--shell",
            shell,
            "--cwd",
            str(workspace),
            command,
        ],
        cwd=BACKEND,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


async def collect_capture(
    tmp_path: Path,
    command: str,
    count: int,
) -> tuple[list[Any], subprocess.Popen[bytes]]:
    endpoint = Path("/tmp") / f"af-provider-{uuid.uuid4()}.sock"
    provider = TerminalProvider(
        tmp_path,
        tmp_path / "legacy.jsonl",
        capture_endpoint=endpoint,
    )
    await provider.initialize()
    await provider.start()
    helper = start_helper(endpoint, tmp_path, command)
    stream = provider.observe()
    observations: list[Any] = []
    try:
        for _ in range(count):
            observations.append(
                await asyncio.wait_for(stream.__anext__(), timeout=2)
            )
    finally:
        await provider.stop()
        await stream.aclose()
    helper.wait(timeout=2)
    helper.communicate(timeout=1)
    return observations, helper


@pytest.mark.asyncio
async def test_provider_consumes_capture_lifecycle_and_output(
    tmp_path: Path,
) -> None:
    observations, helper = await collect_capture(
        tmp_path,
        "printf 'hello\\n'; printf 'error\\n' >&2; sleep 0.2; printf 'world\\n'",
        5,
    )

    assert helper.returncode == 0
    assert [observation.observation_type for observation in observations] == [
        "command.started",
        "terminal.output",
        "terminal.output",
        "terminal.output",
        "command.completed",
    ]
    attributes = [observation.metadata.attributes for observation in observations]
    assert len({item["session_id"] for item in attributes}) == 1
    assert len({item["command_id"] for item in attributes}) == 1
    assert [item["sequence"] for item in attributes] == [1, 2, 3, 4, 5]
    assert {
        (item["stream"], item["text"])
        for item in attributes
        if "stream" in item
    } == {
        ("stdout", "hello\n"),
        ("stderr", "error\n"),
        ("stdout", "world\n"),
    }
    assert attributes[-1]["exit_code"] == 0
    assert all(item["cwd"] == str(tmp_path) for item in attributes)


@pytest.mark.asyncio
async def test_provider_preserves_nonzero_exit_and_stderr_success(
    tmp_path: Path,
) -> None:
    observations, helper = await collect_capture(
        tmp_path,
        "printf 'warning\\n' >&2; exit 7",
        3,
    )

    assert helper.returncode == 7
    assert observations[1].observation_type == "terminal.output"
    assert observations[1].metadata.attributes["stream"] == "stderr"
    assert observations[2].metadata.attributes["exit_code"] == 7


@pytest.mark.asyncio
async def test_provider_filters_capture_events_outside_workspace(
    tmp_path: Path,
) -> None:
    endpoint = Path("/tmp") / f"af-provider-{uuid.uuid4()}.sock"
    provider = TerminalProvider(
        tmp_path,
        tmp_path / "legacy.jsonl",
        capture_endpoint=endpoint,
    )
    await provider.initialize()
    await provider.start()
    stream = provider.observe()

    async def send_event() -> None:
        reader, writer = await asyncio.open_unix_connection(str(endpoint))
        del reader
        event = {
            "version": 1,
            "session_id": "outside-session",
            "command_id": "outside-command",
            "sequence": 1,
            "timestamp": "2026-10-08T00:00:00+00:00",
            "type": "terminal.output",
            "cwd": str(tmp_path.parent),
            "stream": "stdout",
            "text": "outside",
        }
        writer.write((json.dumps(event) + "\n").encode())
        await writer.drain()
        await asyncio.Event().wait()

    sender = asyncio.create_task(send_event())
    try:
        await asyncio.sleep(0.1)
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(stream.__anext__(), timeout=0.1)
    finally:
        await provider.stop()
        await stream.aclose()
        sender.cancel()
        await asyncio.gather(sender, return_exceptions=True)


@pytest.mark.asyncio
async def test_provider_ignores_malformed_and_unsupported_capture_events(
    tmp_path: Path,
) -> None:
    endpoint = Path("/tmp") / f"af-provider-{uuid.uuid4()}.sock"
    provider = TerminalProvider(
        tmp_path,
        tmp_path / "legacy.jsonl",
        capture_endpoint=endpoint,
    )
    await provider.initialize()
    await provider.start()
    stream = provider.observe()
    reader, writer = await asyncio.open_unix_connection(str(endpoint))
    del reader
    writer.write(b"not-json\n")
    writer.write(b'{"type":"unknown"}\n')
    writer.write(
        (
            json.dumps(
                {
                    "version": 1,
                    "session_id": "session",
                    "command_id": "command",
                    "sequence": 1,
                    "timestamp": "2026-10-08T00:00:00+00:00",
                    "type": "command.started",
                    "cwd": str(tmp_path),
                    "command": "true",
                }
            )
            + "\n"
        ).encode()
    )
    await writer.drain()
    try:
        observation = await asyncio.wait_for(stream.__anext__(), timeout=2)
        assert observation.observation_type == "command.started"
    finally:
        await provider.stop()
        await stream.aclose()
        writer.close()
        await writer.wait_closed()


@pytest.mark.asyncio
async def test_provider_reports_capture_disconnect(
    tmp_path: Path,
) -> None:
    endpoint = Path("/tmp") / f"af-provider-{uuid.uuid4()}.sock"
    provider = TerminalProvider(
        tmp_path,
        tmp_path / "legacy.jsonl",
        capture_endpoint=endpoint,
    )
    await provider.initialize()
    await provider.start()
    stream = provider.observe()
    reader, writer = await asyncio.open_unix_connection(str(endpoint))
    del reader
    writer.close()
    await writer.wait_closed()
    try:
        with pytest.raises(RuntimeError, match="capture transport"):
            await asyncio.wait_for(stream.__anext__(), timeout=2)
    finally:
        await provider.stop()
        await stream.aclose()


@pytest.mark.asyncio
async def test_provider_keeps_capture_endpoint_alive_without_connections(
    tmp_path: Path,
) -> None:
    endpoint = Path("/tmp") / f"af-provider-{uuid.uuid4()}.sock"
    provider = TerminalProvider(
        tmp_path,
        tmp_path / "legacy.jsonl",
        capture_endpoint=endpoint,
    )
    await provider.initialize()
    await provider.start()
    stream = provider.observe()
    observer_task = asyncio.create_task(stream.__anext__())

    try:
        await asyncio.sleep(5.2)
        assert endpoint.exists()
    finally:
        observer_task.cancel()
        await asyncio.gather(observer_task, return_exceptions=True)
        await provider.stop()
        await stream.aclose()
