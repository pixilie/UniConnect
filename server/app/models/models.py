import enum
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


# Enums definition
class UserRole(str, enum.Enum):
    ADMIN = "administrator"
    TEACHER = "teacher"
    CLASS_REPR = "class_representative"
    STUDENT = "student"

class MessageType(str, enum.Enum):
    STANDARD = "standard"
    ANNOUNCEMENT = "announcement"

class EventType(str, enum.Enum):
    STUDY = "study_session"
    ACTIVITY = "activity"


# Tables definition
teacher_groups_association = Table(
    "teacher_groups",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("group_id", Integer, ForeignKey("groups.id"), primary_key=True)
)

class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    schedule_path = Column(String, nullable=True)

    students = relationship("User", back_populates="student_group")
    teachers = relationship("User", secondary=teacher_groups_association, back_populates="teaching_groups")
    messages = relationship("Message", back_populates="group")
    events = relationship("Event", back_populates="group")
    assignments = relationship("Assignment", back_populates="group")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role = Column(String, default=UserRole.STUDENT)
    student_group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)

    student_group = relationship("Group", back_populates="students", foreign_keys=[student_group_id])
    teaching_groups = relationship("Group", secondary=teacher_groups_association, back_populates="teachers")
    messages = relationship("Message", back_populates="author")
    created_events = relationship("Event", back_populates="creator")
    created_assignments = relationship("Assignment", back_populates="creator")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    message_type = Column(String, default=MessageType.STANDARD)
    sent_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))

    author = relationship("User", back_populates="messages")
    group = relationship("Group", back_populates="messages")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    date = Column(DateTime, nullable=False)
    location = Column(String, nullable=True)
    type =  Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))

    creator = relationship("User", back_populates="created_events")
    group = relationship("Group", back_populates="events")


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    group_id = Column(Integer, ForeignKey("groups.id"))
    creator_id = Column(Integer, ForeignKey("users.id"))

    group = relationship("Group", back_populates="assignments")
    creator = relationship("User", back_populates="created_assignments")
