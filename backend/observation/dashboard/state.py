from datetime import datetime
from enum import StrEnum
from pathlib import Path


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

    def _trim_observations(self) -> None:
        excess = len(self.observations) - self.max_observations

        if excess > 0:
            del self.observations[:excess]

    def _trim_terminal_log(self) -> None:
        excess = len(self.terminal_log) - self.max_terminal_log

        if excess > 0:
            del self.terminal_log[:excess]
