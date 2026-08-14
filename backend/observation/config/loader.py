from observation.config.settings import ObservationSettings


# =====================================================
# Observation Configuration Loader
# =====================================================


def load_settings() -> ObservationSettings:
    """
    Load Observation Foundation settings.

    Phase 1 uses the default configuration defined by
    ObservationSettings.

    External configuration sources can be introduced
    later without changing the settings model.
    """

    return ObservationSettings()