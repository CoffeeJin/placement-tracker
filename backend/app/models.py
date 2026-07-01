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
    is_active = Column(Integer, default=1)  # 1=active, 0=disabled，先用整型避免布尔在不同库的兼容问题
    created_at = Column(DateTime, default=datetime.utcnow)

    placement_logs = relationship("PlacementLog", back_populates="user", foreign_keys="PlacementLog.user_id")
    reflection_notes = relationship("ReflectionNote", back_populates="user", foreign_keys="ReflectionNote.user_id")
    case_notes = relationship("CaseNote", back_populates="user")


# ---- 预留：supervisor - intern 绑定关系表（MVP 阶段先建空表，不接 API）----
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

    # 预留：审核状态字段，MVP 阶段默认 draft，不做审核界面
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


# ---- 预留：Case Note 表结构，MVP 阶段先建表，不做 API / 界面 ----
class CaseNote(Base):
    __tablename__ = "case_notes"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    case_ref = Column(String(50), nullable=False)  # 内部编号，如 CASE-2026-001
    client_ref = Column(String(50), nullable=False)  # 去标识化的服务对象编号，不存真实姓名
    status = Column(Enum(CaseStatus), nullable=False, default=CaseStatus.ongoing)
    date = Column(Date, nullable=False)
    presenting_issue = Column(Text, nullable=True)
    intervention = Column(Text, nullable=True)
    plan = Column(Text, nullable=True)
    risk_assessment = Column(Text, nullable=True)
    closed_summary = Column(Text, nullable=True)  # 结案说明，status=closed 时建议必填（后续在 API 层加校验）

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="case_notes")


# ---- 预留：case note 与 placement log / reflection note 的关联表（多对多）----
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


# ---- 预留：Feedback 表，MVP 阶段先建表，不接 API ----
class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    note_id = Column(UUID(as_uuid=False), nullable=False)
    note_type = Column(Enum(NoteType), nullable=False)
    supervisor_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    comment = Column(Text, nullable=False)
    is_read = Column(Integer, default=0)  # 0=未读, 1=已读，用于 dashboard todo
    created_at = Column(DateTime, default=datetime.utcnow)
