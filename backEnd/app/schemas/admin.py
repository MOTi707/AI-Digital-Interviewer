from datetime import datetime
from pydantic import BaseModel, Field


# ── Dashboard Stats ────────────────────────────────────

class DashboardStats(BaseModel):
    total_users: int
    total_problems: int
    total_posts: int
    total_interviews: int
    active_users_today: int
    new_users_this_week: int

    class Config:
        from_attributes = True


# ── User Management ────────────────────────────────────

class AdminUserItem(BaseModel):
    id: str
    username: str
    email: str | None
    nickname: str | None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AdminUserListResponse(BaseModel):
    users: list[AdminUserItem]
    total: int
    page: int
    size: int


class AdminUserUpdateRequest(BaseModel):
    is_active: bool | None = None
    nickname: str | None = None


# ── Problem Management ─────────────────────────────────

class AdminProblemCreate(BaseModel):
    display_id: str = Field(..., min_length=1, max_length=20)
    title: str = Field(..., min_length=1, max_length=200)
    description: str
    input_format: str
    output_format: str
    constraints: str
    sample_input: str
    sample_output: str
    hint: str | None = None
    time_limit: int = 1000
    memory_limit: int = 256
    difficulty: str = Field(..., pattern=r"^(easy|medium|hard)$")
    tags: str = ""


class AdminProblemUpdate(BaseModel):
    display_id: str | None = None
    title: str | None = None
    description: str | None = None
    input_format: str | None = None
    output_format: str | None = None
    constraints: str | None = None
    sample_input: str | None = None
    sample_output: str | None = None
    hint: str | None = None
    time_limit: int | None = None
    memory_limit: int | None = None
    difficulty: str | None = None
    tags: str | None = None


class AdminProblemItem(BaseModel):
    id: str
    display_id: str
    title: str
    description: str
    input_format: str
    output_format: str
    constraints: str
    sample_input: str
    sample_output: str
    hint: str | None = None
    time_limit: int
    memory_limit: int
    difficulty: str
    tags: str
    total_submissions: int
    accepted_submissions: int
    created_at: datetime

    class Config:
        from_attributes = True


class AdminProblemListResponse(BaseModel):
    problems: list[AdminProblemItem]
    total: int
    page: int
    size: int


# ── Post Management ────────────────────────────────────

class AdminPostItem(BaseModel):
    id: str
    title: str
    author_id: str
    author_name: str
    company: str
    position: str
    likes_count: int
    comments_count: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class AdminPostListResponse(BaseModel):
    posts: list[AdminPostItem]
    total: int
    page: int
    size: int
