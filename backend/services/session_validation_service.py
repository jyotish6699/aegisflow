from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.session import Session as SessionModel


# =====================================================
# Validate Session Reference
# =====================================================

def validate_session_reference(
    db: Session,
    session_id: UUID,
) -> None:

    session = db.get(
        SessionModel,
        session_id,
    )

    if session is None:

        raise HTTPException(
            status_code=404,
            detail=f"Session '{session_id}' does not exist."
        )