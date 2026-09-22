from pathlib import Path
from unittest.mock import Mock

from observation.lifecycle.starter import ProviderStarter
from observation.lifecycle.stopper import ProviderStopper
from observation.logging.runtime import ObservationRuntime


def test_runtime_accepts_composed_provider_instances() -> None:
    workspace = Path("/tmp/aegisflow")
    providers = [Mock(), Mock()]
    starter = Mock(spec=ProviderStarter)
    stopper = Mock(spec=ProviderStopper)

    runtime = ObservationRuntime(
        workspace,
        providers,
        starter,
        stopper,
    )

    assert runtime.workspace == workspace.resolve()
    assert runtime.providers is providers


def test_runtime_does_not_construct_providers() -> None:
    workspace = Path("/tmp/aegisflow")
    provider_a = Mock()
    provider_b = Mock()
    providers = [provider_a, provider_b]

    starter = Mock(spec=ProviderStarter)
    stopper = Mock(spec=ProviderStopper)

    runtime = ObservationRuntime(
        workspace,
        providers,
        starter,
        stopper,
    )

    assert runtime.providers[0] is provider_a
    assert runtime.providers[1] is provider_b