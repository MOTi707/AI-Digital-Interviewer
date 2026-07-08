import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    display_id: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    input_format: Mapped[str] = mapped_column(Text, nullable=False)
    output_format: Mapped[str] = mapped_column(Text, nullable=False)
    constraints: Mapped[str] = mapped_column(Text, nullable=False)
    sample_input: Mapped[str] = mapped_column(Text, nullable=False)
    sample_output: Mapped[str] = mapped_column(Text, nullable=False)
    hint: Mapped[str | None] = mapped_column(Text, nullable=True)
    time_limit: Mapped[int] = mapped_column(Integer, default=1000)
    memory_limit: Mapped[int] = mapped_column(Integer, default=256)
    difficulty: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )
    tags: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    total_submissions: Mapped[int] = mapped_column(Integer, default=0)
    accepted_submissions: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    submissions = relationship("Submission", back_populates="problem", lazy="noload")


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    problem_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("problems.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    code: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    execution_time: Mapped[int | None] = mapped_column(Integer, nullable=True)
    execution_memory: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    user = relationship("User", lazy="selectin")
    problem = relationship("Problem", back_populates="submissions", lazy="selectin")
