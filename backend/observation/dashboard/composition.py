from pathlib import Path

from observation.composition.composer import ProviderComposer
from observation.composition.factory import ProviderFactory
from observation.config.settings import ObservationSettings
from observation.core.enums import ProviderType
from observation.lifecycle.health import ProviderHealthTracker
from observation.lifecycle.loader import ProviderLoader
from observation.lifecycle.starter import ProviderStarter
from observation.lifecycle.stopper import ProviderStopper
from observation.logging.runtime import ObservationRuntime
from observation.providers.filesystem.provider import FilesystemProvider
from observation.providers.git.provider import GitProvider
from observation.providers.terminal.provider import TerminalProvider
from observation.registry.discovery import discover_providers
from observation.registry.registry import ProviderRegistry


def create_observation_runtime(
    workspace: Path,
    terminal_protocol: Path,
) -> ObservationRuntime:
    discovered = discover_providers(
        [
            GitProvider,
            TerminalProvider,
            FilesystemProvider,
        ]
    )

    factory = ProviderFactory(
        workspace=workspace,
        terminal_protocol=terminal_protocol,
    )

    registry = ProviderRegistry()

    composer = ProviderComposer(
        factory=factory,
        registry=registry,
    )

    composer.compose(discovered)

    settings = ObservationSettings(
        enabled=True,
        providers=[
            ProviderType.GIT,
            ProviderType.TERMINAL,
            ProviderType.FILESYSTEM,
        ],
    )

    loader = ProviderLoader(
        registry=registry,
        settings=settings,
    )

    providers = loader.load()

    health = ProviderHealthTracker()

    starter = ProviderStarter(health)
    stopper = ProviderStopper(health)

    return ObservationRuntime(
        workspace=workspace,
        providers=providers,
        starter=starter,
        stopper=stopper,
    )
