import asyncio
import os
import uuid
from pathlib import Path

import pytest

from observation.providers.terminal.provider import TerminalProvider


BACKEND = Path(__file__).parents[4]
BASH_INTEGRATION = (
    BACKEND / "observation/providers/terminal/bash/integration.sh"
)
ZSH_INTEGRATION = (
    BACKEND / "observation/providers/terminal/zsh/integration.zsh"
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("shell", "integration"),
    [
        ("/usr/bin/bash", BASH_INTEGRATION),
        pytest.param(
            "/usr/bin/zsh",
            ZSH_INTEGRATION,
            marks=pytest.mark.skipif(
                not Path("/usr/bin/zsh").exists(),
                reason="zsh is not installed",
            ),
        ),
    ],
)
async def test_shell_routes_explicit_capture_command(
    tmp_path: Path,
    shell: str,
    integration: Path,
) -> None:
    endpoint = Path("/tmp") / f"af-shell-{uuid.uuid4()}.sock"
    protocol = tmp_path / "legacy.jsonl"
    provider = TerminalProvider(
        tmp_path,
        protocol,
        capture_endpoint=endpoint,
    )
    await provider.initialize()
    await provider.start()

    command = (
        "printf 'hello\\n'; "
        "printf 'error\\n' >&2; "
        "sleep 0.2; "
        "printf 'world\\n'"
    )
    shell_script = (
        f'exec 3>"{protocol}"; '
        f'source "{integration}"; '
        f'aegisflow_capture "{command}"; '
        "printf 'after\\n'"
    )
    environment = {
        **os.environ,
        "AEGISFLOW_TERMINAL_CAPTURE_ENDPOINT": str(endpoint),
        "PYTHONPATH": str(BACKEND),
    }

    process = await asyncio.create_subprocess_exec(
        shell,
        "-c",
        shell_script,
        cwd=tmp_path,
        env=environment,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stream = provider.observe()
    observations = []
    try:
        while True:
            observation = await asyncio.wait_for(
                stream.__anext__(),
                timeout=5,
            )
            if (
                observation.metadata.attributes.get("session_id")
                and observation.observation_type == "command.completed"
            ):
                observations.append(observation)
                break
            if observation.metadata.attributes.get("session_id"):
                observations.append(observation)

        stdout, stderr = await process.communicate()
    finally:
        await provider.stop()
        await stream.aclose()

    capture_types = [item.observation_type for item in observations]
    assert capture_types == [
        "command.started",
        "terminal.output",
        "terminal.output",
        "terminal.output",
        "command.completed",
    ]
    attributes = [item.metadata.attributes for item in observations]
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
    assert attributes[0]["cwd"] == str(tmp_path)
    assert attributes[0]["shell"] == Path(shell).name
    assert attributes[-1]["exit_code"] == 0
    assert stdout == b"hello\nworld\nafter\n"
    assert stderr == b"error\n"
    assert process.returncode == 0


@pytest.mark.asyncio
async def test_bash_capture_preserves_nonzero_exit_status(
    tmp_path: Path,
) -> None:
    endpoint = Path("/tmp") / f"af-shell-{uuid.uuid4()}.sock"
    provider = TerminalProvider(
        tmp_path,
        tmp_path / "legacy.jsonl",
        capture_endpoint=endpoint,
    )
    await provider.initialize()
    await provider.start()
    protocol = tmp_path / "legacy.jsonl"
    environment = {
        **os.environ,
        "AEGISFLOW_TERMINAL_CAPTURE_ENDPOINT": str(endpoint),
        "PYTHONPATH": str(BACKEND),
    }
    script = (
        f'exec 3>"{protocol}"; source "{BASH_INTEGRATION}"; '
        'aegisflow_capture "printf \'before\\n\'; '
        'printf failure >&2; exit 7"; '
        'exit_code=$?; printf "after\\n"; exit "$exit_code"'
    )
    process = await asyncio.create_subprocess_exec(
        "/usr/bin/bash",
        "-c",
        script,
        cwd=tmp_path,
        env=environment,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stream = provider.observe()
    observations = []
    try:
        while True:
            observation = await asyncio.wait_for(
                stream.__anext__(),
                timeout=5,
            )
            if observation.metadata.attributes.get("session_id"):
                observations.append(observation)
            if observation.observation_type == "command.completed":
                break
        stdout, stderr = await process.communicate()
    finally:
        await provider.stop()
        await stream.aclose()

    assert process.returncode == 7
    assert stdout == b"before\nafter\n"
    assert stderr == b"failure"
    assert observations[-1].metadata.attributes["exit_code"] == 7
