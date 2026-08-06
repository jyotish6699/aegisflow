from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from observation.core.metadata import ObservationMetadata
from observation.core.enums import ProviderType


# =====================================================
# Observation
# =====================================================

class Observation(BaseModel):
    """
    Canonical Observation model.
    
    Every Observation Provider must emit this sturcture.
    
    The Observation model represents an objective fact 
    observed from an external system.
    
    It contains no business meaning or interpretation.
    """

    id: UUID = Field(
        default_factory=uuid4
    )

    provider: ProviderType

    observation_type: str

    occurred_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    metadata: ObservationMetadata

