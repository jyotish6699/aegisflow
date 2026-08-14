from pydantic import BaseModel, Field

from observation.core.enums import ProviderType


# =====================================================
# Observation Settings
# =====================================================


class ObservationSettings(BaseModel):
    """
    Configuration for the Observation Foundation.

    This model defines foundation-level settings only.
    Provider-specific configuration belongs to the
    individual provider implementation.
    """

    enabled: bool = True

    providers: list[ProviderType] = Field(
        default_factory=list
    )

    environment: str = "development"