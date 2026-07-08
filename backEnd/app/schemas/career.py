from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ── 请求 ──────────────────────────────────────────────────

class AnswerItem(BaseModel):
    question_id: str = Field(..., description="题目 ID，如 holland_r1")
    score: int = Field(..., ge=1, le=5, description="用户选择的分数 1-5")


class AssessmentSubmitRequest(BaseModel):
    type: str = Field(..., pattern="^(holland|mbti|career_values)$", description="测评类型")
    answers: list[AnswerItem] = Field(..., min_length=1, description="用户答案列表")


# ── 响应 ──────────────────────────────────────────────────

class QuestionOption(BaseModel):
    label: str
    value: int


class QuestionItem(BaseModel):
    id: str
    dimension: str
    text: str
    options: list[QuestionOption]


class AssessmentQuestionsResponse(BaseModel):
    type: str
    title: str
    description: str
    questions: list[QuestionItem]


class AssessmentResponse(BaseModel):
    id: str
    type: str
    result: dict[str, Any]
    summary: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AssessmentListResponse(BaseModel):
    total: int
    items: list[AssessmentResponse]


class CareerRecommendRequest(BaseModel):
    assessment_id: str = Field(..., description="测评记录 ID")
