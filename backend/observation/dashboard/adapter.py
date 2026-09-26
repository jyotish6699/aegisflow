from observation.core.observation import Observation
from observation.dashboard.state import DashboardState


class DashboardObservationAdapter:
    def __init__(self, state: DashboardState) -> None:
        self._state = state

    def apply(self, observation: Observation) -> None:
        self._state.apply_observation(observation)