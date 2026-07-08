import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    author_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # --- 结构化字段 ---
    company: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    position: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    interview_type: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # 远程/线下
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="in_progress", index=True
    )  # offer/waitlist/rejected/in_progress

    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=False)
    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    comments_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    author = relationship("User", lazy="selectin")
    tags = relationship("Tag", secondary="post_tags", lazy="selectin")
    comments = relationship("Comment", back_populates="post", lazy="noload")
    likes = relationship("Like", back_populates="post", lazy="noload")
