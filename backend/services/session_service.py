from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from models.session import Session as SessionModel, SessionStatus
from schemas.session import SessionCreate, SessionUpdate


# -------------------------------------------------
# Create Session
# -------------------------------------------------

def create_session(
    db: Session,
    session_data: SessionCreate,
) -> SessionModel:

    session = SessionModel(
        project_name=session_data.project_name,
        task_name=session_data.task_name,
        notes=session_data.notes,
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


# -------------------------------------------------
# Get Session
# -------------------------------------------------

def get_session(
    db: Session,
    session_id: UUID,
) -> SessionModel | None:

    return (
        db.query(SessionModel)
        .filter(SessionModel.id == session_id)
        .first()
    )


# -------------------------------------------------
# Update Session
# -------------------------------------------------

def update_session(
    db: Session,
    session: SessionModel,
    update_data: SessionUpdate,
) -> SessionModel:

    update_fields = update_data.model_dump(exclude_unset=True)

    for field, value in update_fields.items():
        setattr(session, field, value)

    db.commit()
    db.refresh(session)

    return session


# -------------------------------------------------
# Complete Session
# -------------------------------------------------

def complete_session(
    db: Session,
    session: SessionModel,
) -> SessionModel:

    session.status = SessionStatus.COMPLETED
    session.ended_at = datetime.utcnow()

    db.commit()
    db.refresh(session)

    return session