import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }

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
    job_category: Mapped[str] = mapped_column(String(50), nullable=False)
    job_title: Mapped[str] = mapped_column(String(100), nullable=False)
    # assessment / tech / business / ai_voice_3 / ai_voice_4 / completed
    current_round: Mapped[str] = mapped_column(String(30), nullable=False, default="assessment")
    # in_progress / completed / aborted
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="in_progress", index=True)
    cheat_count: Mapped[int] = mapped_column(Integer, default=0)
    # full = 全流程面试, single = 单轮练习
    interview_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="full")
    # 仅 single 模式有值，指定练习的轮次 key
    target_round: Mapped[str | None] = mapped_column(String(30), nullable=True)
    total_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    # 多维度评分报告 JSON
    report: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    answers = relationship("InterviewAnswer", back_populates="session", lazy="noload")


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    # assessment / tech / business / ai_voice_3 / ai_voice_4
    category: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    # 岗位类别, general 表示通用
    job_category: Mapped[str] = mapped_column(String(50), nullable=False, default="general", index=True)
    # choice / judgment / code / open_ended
    question_type: Mapped[str] = mapped_column(String(20), nullable=False)
    # JSON: 题目内容 { text, options?, ... }
    content: Mapped[dict] = mapped_column(JSON, nullable=False)
    # JSON: 标准答案/评分要点
    answer: Mapped[dict] = mapped_column(JSON, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")


class InterviewAnswer(Base):
    __tablename__ = "interview_answers"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    # assessment / tech / business / ai_voice_3 / ai_voice_4
    round: Mapped[str] = mapped_column(String(30), nullable=False)
    answer_text: Mapped[str] = mapped_column(Text, nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    session = relationship("InterviewSession", back_populates="answers")
