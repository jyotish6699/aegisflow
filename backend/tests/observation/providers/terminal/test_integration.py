import json
import subprocess
from pathlib import Path


def test_bash_emits_command_lifecycle_for_successful_command(
    tmp_path: Path,
) -> None:
    """
    A successfully executed Bash command should produce exactly
    one command.started message and exactly one command.completed
    message.
    """

    integration = (
        Path(__file__).parents[4]
        / "observation"
        / "providers"
        / "terminal"
        / "bash"
        / "integration.sh"
    )

    protocol = tmp_path / "aegisflow-protocol.jsonl"

    result = subprocess.run(
        [
            "bash",
            "-c",
            f"""
            exec 3>"{protocol}"

            source "{integration}"

            printf 'hello'
            """,
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )

    messages = [
        json.loads(line)
        for line in protocol.read_text().splitlines()
        if line.strip()
    ]

    assert result.stdout == "hello"

    started = [
        message
        for message in messages
        if message["type"] == "command.started"
    ]

    completed = [
        message
        for message in messages
        if message["type"] == "command.completed"
    ]

    assert len(started) == 1
    assert len(completed) == 1

    assert started[0]["command"] == "printf 'hello'"
    assert started[0]["cwd"] == str(tmp_path)

    assert completed[0]["command"] == "printf 'hello'"
    assert completed[0]["cwd"] == str(tmp_path)

    assert started[0]["command_id"] == completed[0]["command_id"]

    assert completed[0]["exit_code"] == 0

    assert completed[0]["duration"] >= 0


def test_bash_integration_does_not_emit_observation_when_only_sourced(
    tmp_path: Path,
) -> None:
    """
    Sourcing the Bash integration without executing a developer
    command should not produce a command lifecycle observation.
    """

    integration = (
        Path(__file__).parents[4]
        / "observation"
        / "providers"
        / "terminal"
        / "bash"
        / "integration.sh"
    )

    protocol = tmp_path / "aegisflow-protocol.jsonl"

    subprocess.run(
        [
            "bash",
            "-c",
            f"""
            exec 3>"{protocol}"

            source "{integration}"
            """,
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )

    assert not protocol.read_text().strip()


def test_bash_preserves_command_stderr(
    tmp_path: Path,
) -> None:
    """
    A command's stderr output must remain unchanged while
    the Bash integration continues to emit its lifecycle
    observations.
    """

    integration = (
        Path(__file__).parents[4]
        / "observation"
        / "providers"
        / "terminal"
        / "bash"
        / "integration.sh"
    )

    result = subprocess.run(
        [
            "bash",
            "-c",
            f"""
            source "{integration}"

            printf 'error output' >&2
            """,
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )

    assert "error output" in result.stderr


def test_bash_observations_are_distinguishable_from_command_stderr(
    tmp_path: Path,
) -> None:
    """
    AegisFlow lifecycle observations must be distinguishable
    from ordinary command stderr output.
    """

    integration = (
        Path(__file__).parents[4]
        / "observation"
        / "providers"
        / "terminal"
        / "bash"
        / "integration.sh"
    )

    protocol = tmp_path / "aegisflow-protocol.jsonl"

    result = subprocess.run(
        [
            "bash",
            "-c",
            f"""
            exec 3>"{protocol}"

            source "{integration}"

            printf 'error output' >&2
            """,
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )

    lines = [
        line
        for line in protocol.read_text().splitlines()
        if line.strip()
    ]

    observation_lines = []

    for line in lines:
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue

        if message.get("type") in {
            "command.started",
            "command.completed",
        }:
            observation_lines.append(message)

    assert len(observation_lines) == 2

    assert {
        message["type"]
        for message in observation_lines
    } == {
        "command.started",
        "command.completed",
    }

    assert "error output" in result.stderr


def test_bash_emits_command_lifecycle_for_failed_command(
    tmp_path: Path,
) -> None:
    """
    A failed Bash command should still produce exactly one
    command.started message and exactly one command.completed
    message containing the non-zero exit code.
    """

    integration = (
        Path(__file__).parents[4]
        / "observation"
        / "providers"
        / "terminal"
        / "bash"
        / "integration.sh"
    )

    protocol = tmp_path / "aegisflow-protocol.jsonl"

    result = subprocess.run(
        [
            "bash",
            "-c",
        f"""
        exec 3>"{protocol}"

        source "{integration}"

        false
        """,
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    messages = [
        json.loads(line)
        for line in protocol.read_text().splitlines()
        if line.strip()
    ]

    started = [
        message
        for message in messages
        if message["type"] == "command.started"
    ]

    completed = [
        message
        for message in messages
        if message["type"] == "command.completed"
    ]

    assert len(started) == 1
    assert len(completed) == 1

    assert started[0]["command"] == "false"
    assert completed[0]["command"] == "false"

    assert started[0]["cwd"] == str(tmp_path)
    assert completed[0]["cwd"] == str(tmp_path)

    assert started[0]["command_id"] == completed[0]["command_id"]

    assert completed[0]["exit_code"] != 0
    assert completed[0]["duration"] >= 0