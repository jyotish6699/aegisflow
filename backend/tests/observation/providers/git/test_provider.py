import asyncio
import subprocess
from pathlib import Path

from observation.core.enums import ProviderType
from observation.providers.git.provider import GitProvider


def test_repository_detected(tmp_path: Path) -> None:
    """
    A Git repository should produce exactly one
    repository.detected observation.
    """

    repository = tmp_path / "repository"
    repository.mkdir()

    subprocess.run(
        ["git", "init", str(repository)],
        check=True,
        capture_output=True,
        text=True,
    )

    async def run_provider():
        provider = GitProvider(repository)

        await provider.initialize()
        await provider.start()

        observations = [
            observation
            async for observation in provider.observe()
        ]

        await provider.stop()

        return observations

    observations = asyncio.run(run_provider())

    assert len(observations) == 1

    observation = observations[0]

    assert observation.provider == ProviderType.GIT
    assert observation.observation_type == "repository.detected"

    assert observation.metadata.source == "git"
    assert observation.metadata.version == "1.0"

    assert observation.metadata.attributes["workspace"] == str(
        repository.resolve()
    )

    assert observation.metadata.attributes["repository"] == str(
        repository.resolve()
    )


def test_no_observation_for_non_git_directory(tmp_path: Path) -> None:
    """
    A directory that is not inside a Git repository should
    produce no observations.
    """

    workspace = tmp_path / "non_git_workspace"
    workspace.mkdir()

    async def run_provider():
        provider = GitProvider(workspace)

        await provider.initialize()
        await provider.start()

        observations = [
            observation
            async for observation in provider.observe()
        ]

        await provider.stop()

        return observations

    observations = asyncio.run(run_provider())

    assert observations == []