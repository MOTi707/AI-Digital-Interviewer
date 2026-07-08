import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    Table,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# 多对多关联表
post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", String(36), ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", String(36), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("post_id", "tag_id", name="uq_post_tag"),
)


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    posts = relationship("Post", secondary=post_tags, back_populates="tags", lazy="noload")
