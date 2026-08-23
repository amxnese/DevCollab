from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    projects = relationship("Project", back_populates="owner")
    memberships = relationship("RoomMembership", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    invite_code = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    memberships = relationship("RoomMembership", back_populates="project", cascade="all, delete-orphan")


class RoomMembership(Base):
    __tablename__ = "room_memberships"
    __table_args__ = (UniqueConstraint("project_id", "user_id", name="uq_room_user"),)

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)
    is_admin = Column(Integer, nullable=False, default=0)

    project = relationship("Project", back_populates="memberships")
    user = relationship("User", back_populates="memberships")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    username = Column(String, nullable=False)  # creator; kept denormalized for easy display
    content = Column(String, nullable=False)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    status = Column(String, nullable=True)      # None | "woi" | "completed"
    statusby = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="tasks")
    interactions = relationship("Interaction", back_populates="task", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="task", cascade="all, delete-orphan")


class Interaction(Base):
    __tablename__ = "interactions"
    __table_args__ = (UniqueConstraint("task_id", "username", name="uq_task_user_interaction"),)

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    username = Column(String, nullable=False)
    type = Column(String, nullable=False)  # "like" | "dislike"

    task = relationship("Task", back_populates="interactions")


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    username = Column(String, nullable=False)
    content = Column(String, nullable=False)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="comments")
    interactions = relationship("CommentInteraction", back_populates="comment", cascade="all, delete-orphan")


class CommentInteraction(Base):
    __tablename__ = "comment_interactions"
    __table_args__ = (UniqueConstraint("comment_id", "username", name="uq_comment_user_interaction"),)

    id = Column(Integer, primary_key=True)
    comment_id = Column(Integer, ForeignKey("comments.id"), nullable=False)
    username = Column(String, nullable=False)
    type = Column(String, nullable=False)  # "like" | "dislike"

    comment = relationship("Comment", back_populates="interactions")
