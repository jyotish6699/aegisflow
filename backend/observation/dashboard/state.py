from datetime import datetime
from enum import StrEnum
from pathlib import Path

from observation.core.enums import ProviderType
from observation.core.observation import Observation

class DashboardStatus(StrEnum):
    RUNNING = "running"
    IDLE = "idle"


class ProviderStatus(StrEnum):
    RUNNING = "running"
    IDLE = "idle"


class ProjectState:
    def __init__(
        self,
        name: str,
        path: Path,
        repository: str | None = None,
    ) -> None:
        self.name = name
        self.path = path
        self.repository = repository


class ProviderState:
    def __init__(
        self,
        provider: str,
        status: ProviderStatus = ProviderStatus.IDLE,
        last_activity: datetime | None = None,
        information: str | None = None,
        reason: str | None = None,
    ) -> None:
        self.provider = provider
        self.status = status
        self.last_activity = last_activity
        self.information = information
        self.reason = reason


class ObservationEntry:
    def __init__(
        self,
        timestamp: datetime,
        provider: str,
        observation_type: str,
        rendered_message: str,
    ) -> None:
        self.timestamp = timestamp
        self.provider = provider
        self.observation_type = observation_type
        self.rendered_message = rendered_message


class TerminalLogEntry:
    def __init__(
        self,
        timestamp: datetime,
        message: str,
    ) -> None:
        self.timestamp = timestamp
        self.message = message

class GitProviderState(ProviderState):
    def __init__(
        self,
        status: ProviderStatus = ProviderStatus.IDLE,
        repository: str | None = None,
        branch: str | None = None,
        last_activity: datetime | None = None,
        information: str | None = None,
        reason: str | None = None,
    ) -> None:
        super().__init__(
            provider="git",
            status=status,
            last_activity=last_activity,
            information=information,
            reason=reason,
        )
        self.repository = repository
        self.branch = branch


class TerminalProviderState(ProviderState):
    def __init__(
        self,
        status: ProviderStatus = ProviderStatus.IDLE,
        shell: str | None = None,
        cwd: Path | None = None,
        active_session: bool = False,
        last_activity: datetime | None = None,
        information: str | None = None,
        reason: str | None = None,
    ) -> None:
        super().__init__(
            provider="terminal",
            status=status,
            last_activity=last_activity,
            information=information,
            reason=reason,
        )
        self.shell = shell
        self.cwd = cwd
        self.active_session = active_session


class FilesystemProviderState(ProviderState):
    def __init__(
        self,
        status: ProviderStatus = ProviderStatus.IDLE,
        workspace: Path | None = None,
        last_activity: datetime | None = None,
        event_type: str | None = None,
        information: str | None = None,
        reason: str | None = None,
    ) -> None:
        super().__init__(
            provider="filesystem",
            status=status,
            last_activity=last_activity,
            information=information,
            reason=reason,
        )
        self.workspace = workspace
        self.event_type = event_type


class DashboardState:
    def __init__(
        self,
        project: ProjectState,
        overall_status: DashboardStatus = DashboardStatus.IDLE,
        git: GitProviderState | None = None,
        terminal: TerminalProviderState | None = None,
        filesystem: FilesystemProviderState | None = None,
        observations: list[ObservationEntry] | None = None,
        terminal_log: list[TerminalLogEntry] | None = None,
        max_observations: int = 100,
        max_terminal_log: int = 200,
    ) -> None:
        if max_observations <= 0:
            raise ValueError(
                "max_observations must be greater than zero"
            )

        if max_terminal_log <= 0:
            raise ValueError(
                "max_terminal_log must be greater than zero"
            )

        self.project = project
        self.overall_status = overall_status
        self.git = git or GitProviderState()
        self.terminal = terminal or TerminalProviderState()
        self.filesystem = filesystem or FilesystemProviderState()

        self.max_observations = max_observations
        self.max_terminal_log = max_terminal_log

        self.observations = list(observations or [])
        self.terminal_log = list(terminal_log or [])

        self._trim_observations()
        self._trim_terminal_log()

    def add_observation(
        self,
        observation: ObservationEntry,
    ) -> None:
        self.observations.append(observation)
        self._trim_observations()

    def add_terminal_log(
        self,
        entry: TerminalLogEntry,
    ) -> None:
        self.terminal_log.append(entry)
        self._trim_terminal_log()

    def apply_observation(
        self,
        observation: Observation,
    ) -> None:
        rendered_message = self._render_observation(
            observation
        )

        self.add_observation(
            ObservationEntry(
                timestamp=observation.occurred_at,
                provider=observation.provider.value,
                observation_type=observation.observation_type,
                rendered_message=rendered_message,
            )
        )

        if observation.provider == ProviderType.TERMINAL:
            self._apply_terminal_observation(observation)

            self.add_terminal_log(
                TerminalLogEntry(
                    timestamp=observation.occurred_at,
                    message=rendered_message,
                )
            )

        elif observation.provider == ProviderType.FILESYSTEM:
            self._apply_filesystem_observation(
                observation
            )

        elif observation.provider == ProviderType.GIT:
            self._apply_git_observation(observation)

    def _render_observation(
        self,
        observation: Observation,
    ) -> str:
        attributes = observation.metadata.attributes

        if observation.provider == ProviderType.TERMINAL:
            command = attributes.get("command", "")

            if observation.observation_type == "command.started":
                return f"{command} started"

            if observation.observation_type == "command.completed":
                exit_code = attributes.get("exit_code")

                if exit_code == 0:
                    return f"{command} executed successfully"

                if exit_code is not None:
                    return (
                        f"{command} failed "
                        f"(exit code {exit_code})"
                    )

                return f"{command} executed"

        if observation.provider == ProviderType.FILESYSTEM:
            path = attributes.get("path", "")

            if observation.observation_type == "file.created":
                return f"{path} new created"

            if observation.observation_type == "file.modified":
                return f"{path} updated"

            if observation.observation_type == "file.deleted":
                return f"{path} deleted"

        if observation.provider == ProviderType.GIT:
            if observation.observation_type == "repository.detected":
                repository = attributes.get("repository", "")
                return f"{repository} repository detected"

            if observation.observation_type == "branch.changed":
                branch = attributes.get("branch", "")
                return f"{branch} changed"

            if observation.observation_type == "working_tree.changed":
                clean = attributes.get("working_tree_clean")

                if clean is True:
                    return "working tree clean"

                if clean is False:
                    return "working tree changed"

                return "working tree state changed"

            if observation.observation_type == "commit.changed":
                commit_message = attributes.get(
                    "commit_message"
                )

                if commit_message:
                    return f"{commit_message} committed"

                return "commit changed"

        return observation.observation_type

    def _apply_terminal_observation(
        self,
        observation: Observation,
    ) -> None:
        attributes = observation.metadata.attributes

        self.terminal.cwd = Path(
            attributes["cwd"]
        )

        self.terminal.active_session = True
        self.terminal.last_activity = observation.occurred_at

        shell = attributes.get("shell")

        if shell is not None:
            self.terminal.shell = shell

    def _apply_filesystem_observation(
        self,
        observation: Observation,
    ) -> None:
        attributes = observation.metadata.attributes

        self.filesystem.workspace = Path(
            attributes["workspace"]
        )

        self.filesystem.last_activity = (
            observation.occurred_at
        )

        self.filesystem.event_type = (
            observation.observation_type
        )

    def _apply_git_observation(
        self,
        observation: Observation,
    ) -> None:
        attributes = observation.metadata.attributes

        self.git.last_activity = observation.occurred_at

        repository = attributes.get("repository")

        if repository is not None:
            self.git.repository = repository

        if observation.observation_type == "branch.changed":
            self.git.branch = attributes.get("branch")

        elif observation.observation_type == "repository.detected":
            self.git.repository = attributes.get(
                "repository"
            )

    def _trim_observations(self) -> None:
        excess = len(self.observations) - self.max_observations

        if excess > 0:
            del self.observations[:excess]

    def _trim_terminal_log(self) -> None:
        excess = len(self.terminal_log) - self.max_terminal_log

        if excess > 0:
            del self.terminal_log[:excess]
