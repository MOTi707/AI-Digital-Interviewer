from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ── 请求 ──────────────────────────────────────────────────

class ResumeUploadRequest(BaseModel):
    file_name: str = Field(..., description="文件名")
    raw_text: str = Field(..., description="简历原始文本")


# ── 响应 ──────────────────────────────────────────────────

class ResumeResponse(BaseModel):
    id: str
    file_name: str
    raw_text: str
    file_path: str | None = None
    parsed_content: dict[str, Any] | None = None
    skill_keywords: list[str] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ResumeOptimizeResponse(BaseModel):
    original: list[dict[str, str]] = Field(default_factory=list, description="原文分段")
    optimized: list[dict[str, str]] = Field(default_factory=list, description="优化后分段")
    stats: dict[str, Any] = Field(default_factory=dict, description="优化统计")
