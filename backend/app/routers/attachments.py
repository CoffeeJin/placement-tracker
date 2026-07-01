from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.deps import get_current_user

router = APIRouter(prefix="/attachments", tags=["attachments"])


@router.get("/{attachment_id}/download")
def download_attachment(
    attachment_id: str,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    attachment = db.query(models.Attachment).filter(models.Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    # Authorization: only the note owner can download it (supervisor access is deferred to the review feature).
    if attachment.note_type == models.NoteType.placement_log:
        note = db.query(models.PlacementLog).filter(models.PlacementLog.id == attachment.note_id).first()
    else:
        note = db.query(models.ReflectionNote).filter(models.ReflectionNote.id == attachment.note_id).first()

    if not note or note.user_id != user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to access this attachment")

    return FileResponse(
        attachment.file_path,
        filename=attachment.original_filename,
        media_type=attachment.content_type or "application/octet-stream",
    )
