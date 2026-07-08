from datetime import datetime
from pydantic import BaseModel, Field, field_validator

VALID_LANGUAGES = {"python3", "python", "c", "cpp", "java", "javascript"}


# ---------- Problem Schemas ----------


class ProblemListItem(BaseModel):
    id: str
    display_id: str
    title: str
    difficulty: str
    tags: str
    total_submissions: int
    accepted_submissions: int
    acceptance_rate: float = Field(description="通过率百分比")
    user_solved: bool = Field(False, description="当前用户是否已通过")

    model_config = {"from_attributes": True}


class ProblemListResponse(BaseModel):
    problems: list[ProblemListItem]
    total: int
    page: int
    size: int


class ProblemDetail(BaseModel):
    id: str
    display_id: str
    title: str
    description: str
    input_format: str
    output_format: str
    constraints: str
    sample_input: str
    sample_output: str
    hint: str | None
    time_limit: int
    memory_limit: int
    difficulty: str
    tags: str
    total_submissions: int
    accepted_submissions: int
    acceptance_rate: float
    user_solved: bool = Field(False)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------- Submission Schemas ----------


class SubmissionCreate(BaseModel):
    code: str = Field(..., min_length=1, description="提交的代码")
    language: str = Field(..., min_length=1, max_length=20, description="编程语言")

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        if v.lower() not in VALID_LANGUAGES:
            raise ValueError(f"不支持的语言: {v}，仅支持: python3, c, cpp, java, javascript")
        return v.lower()


class DebugRequest(BaseModel):
    code: str = Field(..., min_length=1, description="调试的代码")
    language: str = Field(..., min_length=1, max_length=20, description="编程语言")
    input_data: str = Field("", description="自定义输入数据")

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        if v.lower() not in VALID_LANGUAGES:
            raise ValueError(f"不支持的语言: {v}，仅支持: python3, c, cpp, java, javascript")
        return v.lower()


class DebugResponse(BaseModel):
    stdout: str = Field("", description="标准输出")
    stderr: str = Field("", description="标准错误")
    exit_code: int = Field(description="退出码")
    execution_time: int = Field(description="执行时间 ms")
    status: str = Field(description="状态: success/compilation_error/runtime_error/time_limit_exceeded")


class SubmissionResponse(BaseModel):
    id: str
    problem_id: str
    code: str
    language: str
    status: str
    execution_time: int | None
    execution_memory: int | None
    error_detail: str = Field("", description="错误详情（编译错误/运行时错误信息）")
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------- Progress Schemas ----------


class DifficultyProgress(BaseModel):
    difficulty: str
    total_problems: int
    solved: int
    attempted: int


class TagProgress(BaseModel):
    tag: str
    total: int
    solved: int


class UserProgressResponse(BaseModel):
    total_submissions: int
    total_accepted: int
    total_problems_attempted: int
    total_problems_solved: int
    by_difficulty: list[DifficultyProgress]
    by_tag: list[TagProgress]
    recent_submissions: list[SubmissionResponse]
