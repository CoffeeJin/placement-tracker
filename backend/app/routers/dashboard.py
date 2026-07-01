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

    # 预留：case note 与 feedback 统计，MVP 阶段功能未上线，暂时恒为 0
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
