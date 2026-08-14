from pydantic import BaseModel, Field


# =====================================================
# Observation Metadata
# =====================================================

class ObservationMetadata(BaseModel):
    """
    Shared metadata attached to every Observation.
    
    Provider-specific information is stored in the
    attributes field.
    """
    version: str = "1.0"

    source: str

    attributes: dict = Field(
        default_factory=dict
    )
