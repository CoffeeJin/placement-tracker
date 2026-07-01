from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=schemas.DashboardSummary)
def summary(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    log_count = db.query(models.PlacementLog).filter(models.PlacementLog.user_id == user.id).count()
    reflection_count = db.query(models.ReflectionNote).filter(models.ReflectionNote.user_id == user.id).count()

    # Reserved: case note and feedback counts. Not yet live in the MVP stage, so always 0 for now.
    open_case_count = 0
    unread_feedback_count = 0

    return schemas.DashboardSummary(
        full_name=user.full_name,
        role=user.role,
        placement_log_count=log_count,
        reflection_note_count=reflection_count,
        open_case_count=open_case_count,
        unread_feedback_count=unread_feedback_count,
    )
