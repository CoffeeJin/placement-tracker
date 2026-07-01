import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.deps import get_current_user
from app.config import settings

router = APIRouter(prefix="/reflection-notes", tags=["reflection-notes"])


def _get_owned_note(db: Session, note_id: str, user: models.User) -> models.ReflectionNote:
    note = db.query(models.ReflectionNote).filter(models.ReflectionNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="记录不存在")
    if note.user_id != user.id:
        raise HTTPException(status_code=403, detail="无权访问此记录")
    return note


@router.get("", response_model=list[schemas.ReflectionNoteOut])
def list_notes(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    notes = (
        db.query(models.ReflectionNote)
        .filter(models.ReflectionNote.user_id == user.id)
        .order_by(models.ReflectionNote.date.desc())
        .all()
    )
    return [_with_attachments(db, n) for n in notes]


@router.post("", response_model=schemas.ReflectionNoteOut)
def create_note(
    payload: schemas.ReflectionNoteCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    note = models.ReflectionNote(user_id=user.id, **payload.model_dump())
    db.add(note)
    db.commit()
    db.refresh(note)
    return _with_attachments(db, note)


@router.get("/{note_id}", response_model=schemas.ReflectionNoteOut)
def get_note(note_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    note = _get_owned_note(db, note_id, user)
    return _with_attachments(db, note)


@router.put("/{note_id}", response_model=schemas.ReflectionNoteOut)
def update_note(
    note_id: str,
    payload: schemas.ReflectionNoteUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    note = _get_owned_note(db, note_id, user)
    if note.status == models.NoteStatus.reviewed:
        raise HTTPException(status_code=400, detail="该记录已审核，无法修改")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(note, field, value)
    db.commit()
    db.refresh(note)
    return _with_attachments(db, note)


@router.delete("/{note_id}")
def delete_note(note_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    note = _get_owned_note(db, note_id, user)
    if note.status == models.NoteStatus.reviewed:
        raise HTTPException(status_code=400, detail="该记录已审核，无法删除")
    db.delete(note)
    db.commit()
    return {"ok": True}


@router.post("/{note_id}/attachments", response_model=schemas.AttachmentOut)
async def upload_attachment(
    note_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    note = _get_owned_note(db, note_id, user)

    contents = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(status_code=400, detail=f"文件超过 {settings.MAX_UPLOAD_SIZE_MB}MB 限制")

    allowed_types = {"image/png", "image/jpeg", "image/gif", "image/webp", "application/pdf",
                      "application/msword",
                      "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="不支持的文件类型")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename)[1]
    stored_name = f"{uuid.uuid4()}{ext}"
    stored_path = os.path.join(settings.UPLOAD_DIR, stored_name)
    with open(stored_path, "wb") as f:
        f.write(contents)

    attachment = models.Attachment(
        note_id=note.id,
        note_type=models.NoteType.reflection_note,
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


def _with_attachments(db: Session, note: models.ReflectionNote) -> models.ReflectionNote:
    note.attachments = (
        db.query(models.Attachment)
        .filter(
            models.Attachment.note_id == note.id,
            models.Attachment.note_type == models.NoteType.reflection_note,
        )
        .all()
    )
    return note
