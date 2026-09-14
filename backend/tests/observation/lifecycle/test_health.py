from observation.core.enums import ProviderType
from observation.lifecycle.health import (
    ProviderHealth,
    ProviderHealthTracker,
)


def test_health_tracker_returns_none_for_untracked_provider() -> None:
    health = ProviderHealthTracker()

    assert health.get_state(ProviderType.GIT) is None


def test_health_tracker_sets_and_gets_state() -> None:
    health = ProviderHealthTracker()

    health.set_state(
        ProviderType.GIT,
        ProviderHealth.INITIALIZING,
    )

    assert (
        health.get_state(ProviderType.GIT)
        == ProviderHealth.INITIALIZING
    )


def test_health_tracker_updates_existing_state() -> None:
    health = ProviderHealthTracker()

    health.set_state(
        ProviderType.GIT,
        ProviderHealth.INITIALIZING,
    )

    health.set_state(
        ProviderType.GIT,
        ProviderHealth.RUNNING,
    )

    assert (
        health.get_state(ProviderType.GIT)
        == ProviderHealth.RUNNING
    )


def test_health_tracker_snapshot_returns_all_states() -> None:
    health = ProviderHealthTracker()

    health.set_state(
        ProviderType.GIT,
        ProviderHealth.RUNNING,
    )

    health.set_state(
        ProviderType.TERMINAL,
        ProviderHealth.READY,
    )

    assert health.snapshot() == {
        ProviderType.GIT: ProviderHealth.RUNNING,
        ProviderType.TERMINAL: ProviderHealth.READY,
    }


def test_health_tracker_snapshot_is_independent() -> None:
    health = ProviderHealthTracker()

    health.set_state(
        ProviderType.GIT,
        ProviderHealth.RUNNING,
    )

    snapshot = health.snapshot()

    snapshot[ProviderType.GIT] = ProviderHealth.FAILED

    assert (
        health.get_state(ProviderType.GIT)
        == ProviderHealth.RUNNING
    )