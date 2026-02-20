import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "administrator"
    TEACHER = "teacher"
    CLASS_REPR = "class_representative"
    STUDENT = "student"

class MessageType(str, enum.Enum):
    STANDARD = "Standard"
    ANNOUNCEMENT = "Announcement"

teacher_classes_association = Table(
    "teacher_classes",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("class_group_id", Integer, ForeignKey("classes.id"), primary_key=True)
)

# Tables definition
class ClassGroup(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    schedule_path = Column(String, nullable=True)

    students = relationship("User", back_populates="student_class", foreign_keys="[User.student_class_id]")
    teachers = relationship(
        "User",
        secondary=teacher_classes_association,
        back_populates="teaching_classes"
    )
    messages = relationship("Message", back_populates="class_group")
    events = relationship("StudyEvent", back_populates="class_group")
    assignments = relationship("Assignment", back_populates="class_group")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role = Column(String, default=UserRole.STUDENT)
    student_class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)

    student_class = relationship(
        "ClassGroup",
        back_populates="students",
        foreign_keys=[student_class_id]
    )
    teaching_classes = relationship(
        "ClassGroup",
        secondary=teacher_classes_association,
        back_populates="teachers"
    )
    messages = relationship("Message", back_populates="author")
    created_events = relationship("StudyEvent", back_populates="creator")
    created_assignments = relationship("Assignment", back_populates="creator")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    message_type = Column(String, default=MessageType.STANDARD)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user_id = Column(Integer, ForeignKey("users.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))

    author = relationship("User", back_populates="messages")
    class_group = relationship("ClassGroup", back_populates="messages")


class Event(Base):
    __tablename__ = "study_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    event_date = Column(DateTime, nullable=False)
    location = Column(String, nullable=True)

    creator_id = Column(Integer, ForeignKey("users.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))

    creator = relationship("User", back_populates="created_events")
    class_group = relationship("ClassGroup", back_populates="events")


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    class_id = Column(Integer, ForeignKey("classes.id"))
    creator_id = Column(Integer, ForeignKey("users.id"))

    class_group = relationship("ClassGroup", back_populates="assignments")
    creator = relationship("User", back_populates="created_assignments")
