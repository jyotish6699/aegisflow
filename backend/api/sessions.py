from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db

from schemas.session import (
    SessionCreate,
    SessionUpdate,
    SessionResponse,
)

from services.session_service import (
    create_session,
    get_session,
    update_session,
    complete_session,
)

router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
)


# -------------------------------------------------
# Create Session
# -------------------------------------------------

@router.post(
    "",
    response_model=SessionResponse,
)
def create_new_session(
    session: SessionCreate,
    db: Session = Depends(get_db),
):
    return create_session(db, session)


# -------------------------------------------------
# Get Session
# -------------------------------------------------

@router.get(
    "/{session_id}",
    response_model=SessionResponse,
)
def get_existing_session(
    session_id: UUID,
    db: Session = Depends(get_db),
):
    session = get_session(db, session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found.",
        )

    return session


# -------------------------------------------------
# Update Session
# -------------------------------------------------

@router.patch(
    "/{session_id}",
    response_model=SessionResponse,
)
def update_existing_session(
    session_id: UUID,
    update: SessionUpdate,
    db: Session = Depends(get_db),
):
    session = get_session(db, session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found.",
        )

    return update_session(
        db,
        session,
        update,
    )


# -------------------------------------------------
# Complete Session
# -------------------------------------------------

@router.post(
    "/{session_id}/complete",
    response_model=SessionResponse,
)
def complete_existing_session(
    session_id: UUID,
    db: Session = Depends(get_db),
):
    session = get_session(db, session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found.",
        )

    return complete_session(
        db,
        session,
    )