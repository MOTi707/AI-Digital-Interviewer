import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Resume(Base):
    __tablename__ = "resumes"

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
        unique=True,  # 每用户只存一条简历
    )
    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="",
    )
    file_path: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        default=None,
    )
    raw_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )
    # 结构化提取结果：{ skills: [], experiences: [], education: [] }
    parsed_content: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )
    # 技能关键词列表
    skill_keywords: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )
    # 措辞优化结果缓存：{ original: [], optimized: [], stats: {} }
    optimized_content: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
