import asyncio
import json
import subprocess
from pathlib import Path

from observation.core.enums import ProviderType
from observation.core.observation import Observation
from observation.providers.terminal.provider import TerminalProvider


def test_terminal_provider_end_to_end_for_successful_command(
    tmp_path: Path,
) -> None:
    """
    A real Bash command should travel through the Bash integration
    protocol and be converted by TerminalProvider into the expected
    command lifecycle observations.
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

    assert result.stdout == "hello"

    async def collect_observations(protocol: Path):
        provider = TerminalProvider(protocol.parent, protocol)

        await provider.initialize()
        await provider.start()

        return [
            observation
            async for observation in provider.observe()
        ]

    observations = asyncio.run(
        collect_observations(protocol)
    )

    assert len(observations) == 2

    started = [
        observation
        for observation in observations
        if observation.observation_type == "command.started"
    ]

    completed = [
        observation
        for observation in observations
        if observation.observation_type == "command.completed"
    ]

    assert len(started) == 1
    assert len(completed) == 1

    started_observation = started[0]
    completed_observation = completed[0]

    assert started_observation.provider == ProviderType.TERMINAL
    assert completed_observation.provider == ProviderType.TERMINAL

    assert started_observation.metadata.source == "terminal"
    assert completed_observation.metadata.source == "terminal"

    started_attributes = started_observation.metadata.attributes
    completed_attributes = completed_observation.metadata.attributes

    assert started_attributes["command"] == "printf 'hello'"
    assert completed_attributes["command"] == "printf 'hello'"

    assert started_attributes["cwd"] == str(tmp_path)
    assert completed_attributes["cwd"] == str(tmp_path)

    assert (
        started_attributes["command_id"]
        == completed_attributes["command_id"]
    )

    assert completed_attributes["exit_code"] == 0
    assert completed_attributes["duration"] >= 0


def test_terminal_provider_end_to_end_for_failed_command(
    tmp_path: Path,
) -> None:
    """
    A failed Bash command should produce a command.started
    observation followed by a command.completed observation
    containing a non-zero exit code.
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

    async def collect_observations(
        protocol: Path,
    ) -> list[Observation]:
        provider = TerminalProvider(tmp_path, protocol)

        await provider.initialize()
        await provider.start()

        return [
            observation
            async for observation in provider.observe()
        ]

    observations = asyncio.run(
        collect_observations(protocol)
    )

    assert result.returncode != 0

    assert len(observations) == 2

    started = observations[0]
    completed = observations[1]

    assert started.provider == ProviderType.TERMINAL
    assert started.observation_type == "command.started"

    assert completed.provider == ProviderType.TERMINAL
    assert completed.observation_type == "command.completed"

    assert started.metadata.source == "terminal"
    assert completed.metadata.source == "terminal"

    assert (
        started.metadata.attributes["command_id"]
        == completed.metadata.attributes["command_id"]
    )

    assert started.metadata.attributes["command"] == "false"
    assert completed.metadata.attributes["command"] == "false"

    assert started.metadata.attributes["cwd"] == str(tmp_path)
    assert completed.metadata.attributes["cwd"] == str(tmp_path)

    assert completed.metadata.attributes["exit_code"] != 0
    assert completed.metadata.attributes["duration"] >= 0