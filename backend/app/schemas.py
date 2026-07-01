from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict

from app.models import UserRole, NoteStatus


# ---------- Auth ----------
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    full_name: str
    role: UserRole
    email: Optional[str] = None


# ---------- Attachment ----------
class AttachmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    original_filename: str
    content_type: Optional[str] = None
    size_bytes: Optional[int] = None
    uploaded_at: datetime


# ---------- PlacementLog ----------
class PlacementLogCreate(BaseModel):
    date: date
    location: str
    topic: str
    placement_type: str
    notes: Optional[str] = None


class PlacementLogUpdate(BaseModel):
    date: Optional[date] = None
    location: Optional[str] = None
    topic: Optional[str] = None
    placement_type: Optional[str] = None
    notes: Optional[str] = None


class PlacementLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    date: date
    location: str
    topic: str
    placement_type: str
    notes: Optional[str] = None
    status: NoteStatus
    created_at: datetime
    updated_at: datetime
    attachments: List[AttachmentOut] = []


# ---------- ReflectionNote ----------
class ReflectionNoteCreate(BaseModel):
    date: date
    location: str
    topic: str
    placement_type: str
    content: Optional[str] = None


class ReflectionNoteUpdate(BaseModel):
    date: Optional[date] = None
    location: Optional[str] = None
    topic: Optional[str] = None
    placement_type: Optional[str] = None
    content: Optional[str] = None


class ReflectionNoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    date: date
    location: str
    topic: str
    placement_type: str
    content: Optional[str] = None
    status: NoteStatus
    created_at: datetime
    updated_at: datetime
    attachments: List[AttachmentOut] = []


# ---------- Dashboard ----------
class DashboardSummary(BaseModel):
    full_name: str
    role: UserRole
    placement_log_count: int
    reflection_note_count: int
    open_case_count: int  # Reserved field, always 0 during the MVP stage
    unread_feedback_count: int  # Reserved field, always 0 during the MVP stage
