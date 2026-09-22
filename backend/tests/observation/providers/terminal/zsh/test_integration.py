import json
import shutil
import subprocess
from pathlib import Path


def zsh_available() -> bool:
    return shutil.which("zsh") is not None


def run_zsh_integration(
    integration: Path,
    protocol: Path,
    command: str,
) -> None:
    script = f"""
exec 3>"{protocol}"
source "{integration}"

_aegisflow_preexec {command!r}

set +e
{command}
_aegisflow_precmd
"""

    result = subprocess.run(
        ["zsh", "-f", "-c", script],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def read_protocol(protocol: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in protocol.read_text().splitlines()
        if line.strip()
    ]


def test_zsh_integration_emits_command_lifecycle(
    tmp_path: Path,
) -> None:
    if not zsh_available():
        return

    integration = (
        Path(__file__).parents[5]
        / "observation"
        / "providers"
        / "terminal"
        / "zsh"
        / "integration.zsh"
    )

    protocol = tmp_path / "aegisflow-terminal.jsonl"

    run_zsh_integration(
        integration,
        protocol,
        "printf 'hello aegisflow'",
    )

    records = read_protocol(protocol)

    started = [
        record
        for record in records
        if record.get("type") == "command.started"
    ]

    completed = [
        record
        for record in records
        if record.get("type") == "command.completed"
    ]

    assert len(started) == 1
    assert len(completed) == 1

    assert started[0]["command"] == "printf 'hello aegisflow'"
    assert completed[0]["command"] == "printf 'hello aegisflow'"

    assert (
        started[0]["command_id"]
        == completed[0]["command_id"]
    )

    assert started[0]["cwd"] == str(Path.cwd())
    assert completed[0]["cwd"] == str(Path.cwd())

    assert completed[0]["exit_code"] == 0
    assert completed[0]["duration"] >= 0


def test_zsh_integration_emits_nonzero_exit_code(
    tmp_path: Path,
) -> None:
    if not zsh_available():
        return

    integration = (
        Path(__file__).parents[5]
        / "observation"
        / "providers"
        / "terminal"
        / "zsh"
        / "integration.zsh"
    )

    protocol = tmp_path / "aegisflow-terminal.jsonl"

    run_zsh_integration(
        integration,
        protocol,
        "false",
    )

    records = read_protocol(protocol)

    started = [
        record
        for record in records
        if record.get("type") == "command.started"
    ]

    completed = [
        record
        for record in records
        if record.get("type") == "command.completed"
    ]

    assert len(started) == 1
    assert len(completed) == 1

    assert started[0]["command"] == "false"
    assert completed[0]["command"] == "false"

    assert (
        started[0]["command_id"]
        == completed[0]["command_id"]
    )

    assert completed[0]["exit_code"] == 1
    assert completed[0]["duration"] >= 0