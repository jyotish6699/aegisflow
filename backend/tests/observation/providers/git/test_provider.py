import asyncio
import subprocess
from pathlib import Path

from observation.core.enums import ProviderType
from observation.providers.git.provider import GitProvider


def initialize_git_repository(repository: Path) -> str:
    """
    Create a Git repository with one initial commit.

    Returns the initial commit SHA.
    """

    subprocess.run(
        ["git", "init", str(repository)],
        check=True,
        capture_output=True,
        text=True,
    )

    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "config",
            "user.name",
            "AegisFlow Test",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "config",
            "user.email",
            "test@aegisflow.local",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    initial_file = repository / "initial.txt"
    initial_file.write_text("initial")

    subprocess.run(
        ["git", "-C", str(repository), "add", "."],
        check=True,
        capture_output=True,
        text=True,
    )

    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "commit",
            "-m",
            "feat(git): initial repository",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    return subprocess.run(
        ["git", "-C", str(repository), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


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


def test_branch_changed_observation(tmp_path: Path) -> None:
    """
    A branch change should produce exactly one
    branch.changed observation containing the actual
    branch name.
    """

    repository = tmp_path / "repository"
    repository.mkdir()

    subprocess.run(
        ["git", "init", str(repository)],
        check=True,
        capture_output=True,
        text=True,
    )

    subprocess.run(
        ["git", "-C", str(repository), "config", "user.name", "Test User"],
        check=True,
    )

    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "config",
            "user.email",
            "test@example.com",
        ],
        check=True,
    )

    (repository / "README.md").write_text("initial\n")

    subprocess.run(
        ["git", "-C", str(repository), "add", "README.md"],
        check=True,
    )

    subprocess.run(
        ["git", "-C", str(repository), "commit", "-m", "initial commit"],
        check=True,
        capture_output=True,
        text=True,
    )

    async def run_provider():
        provider = GitProvider(repository)

        await provider.initialize()
        await provider.start()

        # Consume the initial repository.detected observation.
        initial_observations = [
            observation
            async for observation in provider.observe()
        ]

        assert len(initial_observations) == 1
        assert initial_observations[0].observation_type == "repository.detected"

        subprocess.run(
            [
                "git",
                "-C",
                str(repository),
                "switch",
                "-c",
                "feature/test-branch",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        observations = [
            observation
            async for observation in provider.observe()
        ]

        await provider.stop()

        return observations

    observations = asyncio.run(run_provider())

    assert len(observations) == 1

    observation = observations[0]

    assert observation.observation_type == "branch.changed"
    assert observation.metadata.attributes["branch"] == "feature/test-branch"


def test_no_observation_when_branch_unchanged(tmp_path: Path) -> None:
    """
    No branch.changed observation should be produced when
    the repository remains on the same branch.
    """

    repository = tmp_path / "repository"
    repository.mkdir()

    subprocess.run(
        ["git", "init", str(repository)],
        check=True,
        capture_output=True,
        text=True,
    )

    subprocess.run(
        ["git", "-C", str(repository), "config", "user.name", "Test User"],
        check=True,
    )

    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "config",
            "user.email",
            "test@example.com",
        ],
        check=True,
    )

    (repository / "README.md").write_text("initial\n")

    subprocess.run(
        ["git", "-C", str(repository), "add", "README.md"],
        check=True,
    )

    subprocess.run(
        ["git", "-C", str(repository), "commit", "-m", "initial commit"],
        check=True,
        capture_output=True,
        text=True,
    )

    async def run_provider():
        provider = GitProvider(repository)

        await provider.initialize()
        await provider.start()

        # Consume repository.detected.
        async for _ in provider.observe():
            pass

        # Same branch, so no branch.changed event.
        observations = [
            observation
            async for observation in provider.observe()
        ]

        await provider.stop()

        return observations

    observations = asyncio.run(run_provider())

    assert observations == []


def test_working_tree_changed_to_dirty(tmp_path: Path) -> None:
    """
    A clean working tree becoming dirty should produce
    a working_tree.changed observation containing the
    actual current state.
    """

    repository = tmp_path / "repository"
    repository.mkdir()

    subprocess.run(
        ["git", "init", str(repository)],
        check=True,
        capture_output=True,
        text=True,
    )

    subprocess.run(
        ["git", "-C", str(repository), "config", "user.name", "Test User"],
        check=True,
    )

    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "config",
            "user.email",
            "test@example.com",
        ],
        check=True,
    )

    (repository / "README.md").write_text("initial\n")

    subprocess.run(
        ["git", "-C", str(repository), "add", "README.md"],
        check=True,
    )

    subprocess.run(
        ["git", "-C", str(repository), "commit", "-m", "initial commit"],
        check=True,
        capture_output=True,
        text=True,
    )

    async def run_provider():
        provider = GitProvider(repository)

        await provider.initialize()
        await provider.start()

        async for _ in provider.observe():
            pass

        (repository / "README.md").write_text("changed\n")

        observations = [
            observation
            async for observation in provider.observe()
        ]

        await provider.stop()

        return observations

    observations = asyncio.run(run_provider())

    assert len(observations) == 1

    observation = observations[0]

    assert observation.observation_type == "working_tree.changed"
    assert observation.metadata.attributes["working_tree_clean"] is False


def test_working_tree_changed_to_clean(tmp_path: Path) -> None:
    """
    A dirty working tree becoming clean should produce
    a working_tree.changed observation containing the
    actual current state.
    """

    repository = tmp_path / "repository"
    repository.mkdir()

    subprocess.run(
        ["git", "init", str(repository)],
        check=True,
        capture_output=True,
        text=True,
    )

    subprocess.run(
        ["git", "-C", str(repository), "config", "user.name", "Test User"],
        check=True,
    )

    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "config",
            "user.email",
            "test@example.com",
        ],
        check=True,
    )

    (repository / "README.md").write_text("initial\n")

    subprocess.run(
        ["git", "-C", str(repository), "add", "README.md"],
        check=True,
    )

    subprocess.run(
        ["git", "-C", str(repository), "commit", "-m", "initial commit"],
        check=True,
        capture_output=True,
        text=True,
    )

    async def run_provider():
        provider = GitProvider(repository)

        await provider.initialize()
        await provider.start()

        async for _ in provider.observe():
            pass

        # clean → dirty
        (repository / "README.md").write_text("changed\n")

        dirty_observations = [
            observation
            async for observation in provider.observe()
        ]

        assert len(dirty_observations) == 1
        assert (
            dirty_observations[0].observation_type
            == "working_tree.changed"
        )
        assert (
            dirty_observations[0].metadata.attributes["working_tree_clean"]
            is False
        )

        # dirty → clean
        subprocess.run(
            ["git", "-C", str(repository), "checkout", "--", "README.md"],
            check=True,
        )

        clean_observations = [
            observation
            async for observation in provider.observe()
        ]

        await provider.stop()

        return clean_observations

    observations = asyncio.run(run_provider())

    assert len(observations) == 1

    observation = observations[0]

    assert observation.observation_type == "working_tree.changed"
    assert observation.metadata.attributes["working_tree_clean"] is True


def test_commit_changed_observation(tmp_path: Path) -> None:
    """
    A new Git commit should produce exactly one
    commit.changed observation containing the new
    commit SHA and commit message.
    """

    repository = tmp_path / "repository"
    repository.mkdir()

    initialize_git_repository(repository)

    async def run_provider():
        provider = GitProvider(repository)

        await provider.initialize()
        await provider.start()

        # Consume the initial repository.detected observation.
        initial_observations = [
            observation
            async for observation in provider.observe()
        ]

        assert len(initial_observations) == 1
        assert initial_observations[0].observation_type == "repository.detected"

        # Create a new commit.
        file = repository / "initial.txt"
        file.write_text("updated")

        subprocess.run(
            ["git", "-C", str(repository), "add", "."],
            check=True,
            capture_output=True,
            text=True,
        )

        subprocess.run(
            [
                "git",
                "-C",
                str(repository),
                "commit",
                "-m",
                "feat(git): update repository",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        expected_commit = subprocess.run(
            ["git", "-C", str(repository), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

        observations = [
            observation
            async for observation in provider.observe()
        ]

        await provider.stop()

        return observations, expected_commit

    observations, expected_commit = asyncio.run(run_provider())

    assert len(observations) == 1

    observation = observations[0]

    assert observation.observation_type == "commit.changed"
    assert observation.provider == ProviderType.GIT

    assert observation.metadata.attributes["commit"] == expected_commit
    assert (
        observation.metadata.attributes["commit_message"]
        == "feat(git): update repository"
    )


def test_commit_changed_observation(tmp_path: Path) -> None:
    """
    GitProvider should emit a commit.changed observation when
    a new commit is created after initialization.
    """

    repository = tmp_path / "repository"
    repository.mkdir()

    subprocess.run(
        ["git", "init", str(repository)],
        check=True,
        capture_output=True,
        text=True,
    )

    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "config",
            "user.name",
            "AegisFlow Test",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "config",
            "user.email",
            "test@aegisflow.local",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    initial_file = repository / "initial.txt"
    initial_file.write_text("initial")

    subprocess.run(
        ["git", "-C", str(repository), "add", "."],
        check=True,
        capture_output=True,
        text=True,
    )

    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "commit",
            "-m",
            "feat(git): initial repository",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    async def run_provider():
        provider = GitProvider(repository)

        await provider.initialize()
        await provider.start()

        # First observation establishes repository detection.
        observations = [
            observation
            async for observation in provider.observe()
        ]

        assert len(observations) == 1
        assert observations[0].observation_type == "repository.detected"

        # Create a new commit.
        initial_file.write_text("updated")

        subprocess.run(
            ["git", "-C", str(repository), "add", "."],
            check=True,
            capture_output=True,
            text=True,
        )

        commit_message = "feat(git): update repository"

        subprocess.run(
            [
                "git",
                "-C",
                str(repository),
                "commit",
                "-m",
                commit_message,
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        expected_commit = subprocess.run(
            ["git", "-C", str(repository), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

        # The second observation cycle should detect the new commit.
        observations = [
            observation
            async for observation in provider.observe()
        ]

        await provider.stop()

        return observations, expected_commit, commit_message

    observations, expected_commit, commit_message = asyncio.run(run_provider())

    assert len(observations) == 1

    observation = observations[0]

    assert observation.observation_type == "commit.changed"
    assert observation.metadata.attributes["commit"] == expected_commit
    assert observation.metadata.attributes["commit_message"] == commit_message