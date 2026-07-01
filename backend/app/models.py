import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, DateTime, Date, Text, ForeignKey, Enum, Integer
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class UserRole(str, enum.Enum):
    student = "student"
    supervisor = "supervisor"
    admin = "admin"


class NoteStatus(str, enum.Enum):
    draft = "draft"
    submitted = "submitted"
    reviewed = "reviewed"


class CaseStatus(str, enum.Enum):
    ongoing = "ongoing"
    closed = "closed"


class NoteType(str, enum.Enum):
    placement_log = "placement_log"
    reflection_note = "reflection_note"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(120), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.student)
    is_active = Column(Integer, default=1)  # 1=active, 0=disabled; using an integer to avoid boolean compatibility issues across databases
    created_at = Column(DateTime, default=datetime.utcnow)

    placement_logs = relationship("PlacementLog", back_populates="user", foreign_keys="PlacementLog.user_id")
    reflection_notes = relationship("ReflectionNote", back_populates="user", foreign_keys="ReflectionNote.user_id")
    case_notes = relationship("CaseNote", back_populates="user")


# ---- Reserved: supervisor-intern binding table (empty table for now during MVP stage, no API) ----
class SupervisorIntern(Base):
    __tablename__ = "supervisor_interns"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    supervisor_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    intern_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class PlacementLog(Base):
    __tablename__ = "placement_logs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    location = Column(String(200), nullable=False)
    topic = Column(String(200), nullable=False)
    placement_type = Column(String(100), nullable=False)
    notes = Column(Text, nullable=True)

    # Reserved: review status field, defaults to draft during the MVP stage; no review UI yet
    status = Column(Enum(NoteStatus), nullable=False, default=NoteStatus.draft)
    reviewer_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="placement_logs", foreign_keys=[user_id])


class ReflectionNote(Base):
    __tablename__ = "reflection_notes"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    location = Column(String(200), nullable=False)
    topic = Column(String(200), nullable=False)
    placement_type = Column(String(100), nullable=False)
    content = Column(Text, nullable=True)

    status = Column(Enum(NoteStatus), nullable=False, default=NoteStatus.draft)
    reviewer_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="reflection_notes", foreign_keys=[user_id])


# ---- Reserved: Case Note table structure. Table is created during MVP stage, no API / UI yet ----
class CaseNote(Base):
    __tablename__ = "case_notes"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    case_ref = Column(String(50), nullable=False)  # internal reference number, e.g. CASE-2026-001
    client_ref = Column(String(50), nullable=False)  # de-identified client reference; real names are not stored
    status = Column(Enum(CaseStatus), nullable=False, default=CaseStatus.ongoing)
    date = Column(Date, nullable=False)
    presenting_issue = Column(Text, nullable=True)
    intervention = Column(Text, nullable=True)
    plan = Column(Text, nullable=True)
    risk_assessment = Column(Text, nullable=True)
    closed_summary = Column(Text, nullable=True)  # case closure summary; should be required when status=closed (add validation at the API layer later)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="case_notes")


# ---- Reserved: many-to-many link table between case notes and placement logs / reflection notes ----
class CaseNoteLink(Base):
    __tablename__ = "case_note_links"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    case_note_id = Column(UUID(as_uuid=False), ForeignKey("case_notes.id"), nullable=False)
    linked_note_id = Column(UUID(as_uuid=False), nullable=False)
    linked_note_type = Column(Enum(NoteType), nullable=False)


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    note_id = Column(UUID(as_uuid=False), nullable=False)
    note_type = Column(Enum(NoteType), nullable=False)
    file_path = Column(String(500), nullable=False)
    original_filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=True)
    size_bytes = Column(Integer, nullable=True)
    uploaded_by = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)


# ---- Reserved: Feedback table. Table is created during MVP stage, no API yet ----
class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    note_id = Column(UUID(as_uuid=False), nullable=False)
    note_type = Column(Enum(NoteType), nullable=False)
    supervisor_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    comment = Column(Text, nullable=False)
    is_read = Column(Integer, default=0)  # 0=unread, 1=read; used for the dashboard todo list
    created_at = Column(DateTime, default=datetime.utcnow)
