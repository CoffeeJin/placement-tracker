import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.deps import get_current_user
from app.config import settings

router = APIRouter(prefix="/placement-logs", tags=["placement-logs"])


def _get_owned_log(db: Session, log_id: str, user: models.User) -> models.PlacementLog:
    log = db.query(models.PlacementLog).filter(models.PlacementLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Record not found")
    # Data isolation: users can only operate on their own records (supervisor read access is deferred to the review feature).
    if log.user_id != user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to access this record")
    return log


@router.get("", response_model=list[schemas.PlacementLogOut])
def list_logs(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    logs = (
        db.query(models.PlacementLog)
        .filter(models.PlacementLog.user_id == user.id)
        .order_by(models.PlacementLog.date.desc())
        .all()
    )
    return [_with_attachments(db, log) for log in logs]


@router.post("", response_model=schemas.PlacementLogOut)
def create_log(
    payload: schemas.PlacementLogCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    log = models.PlacementLog(user_id=user.id, **payload.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return _with_attachments(db, log)


@router.get("/{log_id}", response_model=schemas.PlacementLogOut)
def get_log(log_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    log = _get_owned_log(db, log_id, user)
    return _with_attachments(db, log)


@router.put("/{log_id}", response_model=schemas.PlacementLogOut)
def update_log(
    log_id: str,
    payload: schemas.PlacementLogUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    log = _get_owned_log(db, log_id, user)
    # Reviewed records are locked and cannot be modified (a rule reserved for the future review feature;
    # status is always draft during the MVP stage, so this does not affect current usage).
    if log.status == models.NoteStatus.reviewed:
        raise HTTPException(status_code=400, detail="This record has already been reviewed and cannot be modified")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(log, field, value)
    db.commit()
    db.refresh(log)
    return _with_attachments(db, log)


@router.delete("/{log_id}")
def delete_log(log_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    log = _get_owned_log(db, log_id, user)
    if log.status == models.NoteStatus.reviewed:
        raise HTTPException(status_code=400, detail="This record has already been reviewed and cannot be deleted")
    db.delete(log)
    db.commit()
    return {"ok": True}


@router.post("/{log_id}/attachments", response_model=schemas.AttachmentOut)
async def upload_attachment(
    log_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    log = _get_owned_log(db, log_id, user)

    contents = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(status_code=400, detail=f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB limit")

    allowed_types = {"image/png", "image/jpeg", "image/gif", "image/webp", "application/pdf",
                      "application/msword",
                      "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename)[1]
    stored_name = f"{uuid.uuid4()}{ext}"
    stored_path = os.path.join(settings.UPLOAD_DIR, stored_name)
    with open(stored_path, "wb") as f:
        f.write(contents)

    attachment = models.Attachment(
        note_id=log.id,
        note_type=models.NoteType.placement_log,
        file_path=stored_path,
        original_filename=file.filename,
        content_type=file.content_type,
        size_bytes=len(contents),
        uploaded_by=user.id,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment


def _with_attachments(db: Session, log: models.PlacementLog) -> models.PlacementLog:
    log.attachments = (
        db.query(models.Attachment)
        .filter(
            models.Attachment.note_id == log.id,
            models.Attachment.note_type == models.NoteType.placement_log,
        )
        .all()
    )
    return log
