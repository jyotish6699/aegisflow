from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db

from services.timeline_service import build_timeline

from schemas.timeline import Timeline


router = APIRouter(

    prefix="/timeline",

    tags=["Timeline"],

)


@router.get(

    "/{session_id}",

    response_model=Timeline,

)

def get_timeline(

    session_id: UUID,

    db: Session = Depends(get_db),

):

    return build_timeline(

        db=db,

        session_id=session_id,

    )