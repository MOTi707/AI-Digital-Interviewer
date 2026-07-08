import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CareerAssessment(Base):
    __tablename__ = "career_assessments"

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
    # holland | mbti | career_values
    type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
    )
    # 原始答案：[{ question_id, score }, ...]
    answers: Mapped[dict | list] = mapped_column(
        JSON,
        nullable=False,
    )
    # 计算后的结构化结果
    result: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )
    # 结果摘要文本
    summary: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )
    # AI 岗位推荐缓存：{ jobs: [...], prep_tips: [...] }
    recommendation: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
