import subprocess
from pathlib import Path

from observation.providers.git.state import GitState
from observation.providers.git.exceptions import GitStateUnavailableError

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
        ["git", "-C", str(repository), "config", "user.name", "AegisFlow Test"],
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

    commit = subprocess.run(
        ["git", "-C", str(repository), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    return commit


def test_git_state_reads_clean_repository(tmp_path: Path) -> None:
    """
    GitState should correctly read a clean Git repository.
    """

    repository = tmp_path / "repository"
    repository.mkdir()

    expected_commit = initialize_git_repository(repository)

    state = GitState.read(repository)

    branch = subprocess.run(
        ["git", "-C", str(repository), "branch", "--show-current"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    assert state.branch == branch
    assert state.working_tree_clean is True
    assert state.commit == expected_commit
    assert state.commit_message == "feat(git): initial repository"


def test_git_state_detects_dirty_working_tree(tmp_path: Path) -> None:
    """
    GitState should report a dirty working tree when a file changes.
    """

    repository = tmp_path / "repository"
    repository.mkdir()

    initialize_git_repository(repository)

    file = repository / "initial.txt"
    file.write_text("modified")

    state = GitState.read(repository)

    assert state.working_tree_clean is False


def test_git_state_unavailable_for_unborn_repository(
    tmp_path: Path,
) -> None:
    """
    GitState should report unavailable state when a repository
    has been initialized but has no commit yet.
    """

    repository = tmp_path / "repository"
    repository.mkdir()

    subprocess.run(
        ["git", "init", str(repository)],
        check=True,
        capture_output=True,
        text=True,
    )

    try:
        GitState.read(repository)
    except GitStateUnavailableError:
        return

    raise AssertionError(
        "GitState.read() should raise GitStateUnavailableError "
        "for an unborn repository."
    )