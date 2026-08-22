import asyncio
import subprocess
from pathlib import Path

from observation.core.enums import ProviderType
from observation.providers.git.provider import GitProvider


def configure_git_repository(repository: Path) -> None:
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


def commit(
    repository: Path,
    message: str,
) -> str:
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
            message,
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    return subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "rev-parse",
            "HEAD",
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def test_git_provider_end_to_end(tmp_path: Path) -> None:
    """
    Verify the complete Git Provider observation lifecycle
    from repository detection through branch, working-tree,
    commit changes, and provider shutdown.
    """

    repository = tmp_path / "repository"
    repository.mkdir()

    # -------------------------------------------------
    # 1. Create Git repository
    # -------------------------------------------------

    subprocess.run(
        ["git", "init", str(repository)],
        check=True,
        capture_output=True,
        text=True,
    )

    configure_git_repository(repository)

    # -------------------------------------------------
    # 2. Initial commit
    # -------------------------------------------------

    initial_file = repository / "README.md"
    initial_file.write_text("initial\n")

    initial_commit = commit(
        repository,
        "feat(git): initialize repository",
    )

    # -------------------------------------------------
    # 3. Start provider
    # -------------------------------------------------

    async def run_provider():
        provider = GitProvider(repository)

        await provider.initialize()

        # Provider must not observe before start.
        before_start = [
            observation
            async for observation in provider.observe()
        ]

        await provider.start()

        # -------------------------------------------------
        # 4. Repository detection
        # -------------------------------------------------

        repository_observations = [
            observation
            async for observation in provider.observe()
        ]

        # -------------------------------------------------
        # 5. No duplicate repository detection
        # -------------------------------------------------

        duplicate_observations = [
            observation
            async for observation in provider.observe()
        ]

        # -------------------------------------------------
        # 6. Branch change
        # -------------------------------------------------

        subprocess.run(
            [
                "git",
                "-C",
                str(repository),
                "switch",
                "-c",
                "feature/e2e-test",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        branch_observations = [
            observation
            async for observation in provider.observe()
        ]

        # -------------------------------------------------
        # 7. Working-tree change
        # -------------------------------------------------

        initial_file.write_text("modified\n")

        dirty_observations = [
            observation
            async for observation in provider.observe()
        ]

        # -------------------------------------------------
        # 8. Commit the file change
        # -------------------------------------------------

        commit_message = "feat(git): update repository"

        expected_commit = commit(
            repository,
            commit_message,
        )

        # The commit makes the working tree clean again.
        post_commit_working_tree_observations = [
            observation
            async for observation in provider.observe()
        ]

        # The next observation cycle detects the new commit.
        commit_observations = [
            observation
            async for observation in provider.observe()
        ]

        assert len(post_commit_working_tree_observations) == 1
        assert (
            post_commit_working_tree_observations[0].observation_type
            == "working_tree.changed"
        )

        assert len(commit_observations) == 1
        assert (
            commit_observations[0].observation_type
            == "commit.changed"
        )

        assert commit_observations[0].metadata.attributes == {
            "workspace": str(repository.resolve()),
            "repository": str(repository.resolve()),
            "commit": expected_commit,
            "commit_message": commit_message,
        }

        assert (
            post_commit_working_tree_observations[0].metadata.attributes
            == {
                "workspace": str(repository.resolve()),
                "repository": str(repository.resolve()),
                "working_tree_clean": True,
            }
        )

        # -------------------------------------------------
        # 9. Stop provider
        # -------------------------------------------------

        await provider.stop()

        after_stop = [
            observation
            async for observation in provider.observe()
        ]

        return (
            before_start,
            repository_observations,
            duplicate_observations,
            branch_observations,
            dirty_observations,
            commit_observations,
            after_stop,
            initial_commit,
            expected_commit,
            commit_message,
        )

    (
        before_start,
        repository_observations,
        duplicate_observations,
        branch_observations,
        dirty_observations,
        commit_observations,
        after_stop,
        initial_commit,
        expected_commit,
        commit_message,
    ) = asyncio.run(run_provider())

    # -------------------------------------------------
    # Final verification
    # -------------------------------------------------

    assert before_start == []

    assert len(repository_observations) == 1

    assert repository_observations[0].provider == ProviderType.GIT
    assert (
        repository_observations[0].observation_type
        == "repository.detected"
    )

    assert duplicate_observations == []

    assert len(branch_observations) == 1
    assert branch_observations[0].observation_type == "branch.changed"

    assert branch_observations[0].metadata.attributes == {
        "workspace": str(repository.resolve()),
        "repository": str(repository.resolve()),
        "branch": "feature/e2e-test",
    }

    assert len(dirty_observations) == 1
    assert (
        dirty_observations[0].observation_type
        == "working_tree.changed"
    )

    assert dirty_observations[0].metadata.attributes == {
        "workspace": str(repository.resolve()),
        "repository": str(repository.resolve()),
        "working_tree_clean": False,
    }

    assert len(commit_observations) == 1
    assert commit_observations[0].observation_type == "commit.changed"

    assert commit_observations[0].metadata.attributes == {
        "workspace": str(repository.resolve()),
        "repository": str(repository.resolve()),
        "commit": expected_commit,
        "commit_message": commit_message,
    }

    assert expected_commit != initial_commit

    assert after_stop == []