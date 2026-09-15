from collections.abc import Iterable
from pathlib import Path

from observation.core.provider import ObservationProvider
from observation.providers.filesystem.provider import FilesystemProvider
from observation.providers.git.provider import GitProvider
from observation.providers.terminal.provider import TerminalProvider


class ProviderFactory:
    """
    Constructs Observation Provider instances.

    The factory is responsible only for provider construction.
    It does not discover, register, load, initialize, start,
    observe, stop, or interpret providers.
    """

    def __init__(
        self,
        workspace: Path,
        terminal_protocol: Path,
    ) -> None:
        self._workspace = workspace.resolve()
        self._terminal_protocol = terminal_protocol.resolve()

    def create(
        self,
        providers: Iterable[type[ObservationProvider]],
    ) -> list[ObservationProvider]:
        """
        Construct provider instances from provider classes.
        """

        instances: list[ObservationProvider] = []

        for provider in providers:
            if provider is GitProvider:
                instances.append(
                    GitProvider(self._workspace)
                )
                continue

            if provider is TerminalProvider:
                instances.append(
                    TerminalProvider(
                        self._workspace,
                        self._terminal_protocol,
                    )
                )
                continue

            if provider is FilesystemProvider:
                instances.append(
                    FilesystemProvider(self._workspace)
                )
                continue

            raise ValueError(
                f"Unsupported provider class: {provider.__name__}"
            )

        return instances