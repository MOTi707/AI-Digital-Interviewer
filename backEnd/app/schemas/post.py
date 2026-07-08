from datetime import datetime
from pydantic import BaseModel, Field


class TagResponse(BaseModel):
    id: str
    name: str
    model_config = {"from_attributes": True}


class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="标题")
    content: str = Field(..., min_length=10, description="正文内容")

    # 结构化字段
    company: str = Field(..., min_length=1, max_length=100, description="公司")
    position: str = Field(..., min_length=1, max_length=100, description="岗位")
    year: int = Field(..., ge=2020, le=2030, description="年份")
    interview_type: str | None = Field(None, description="面试类型：远程/线下")
    status: str = Field(
        "in_progress",
        description="状态：offer/waitlist/rejected/in_progress",
    )

    is_anonymous: bool = Field(False, description="是否匿名发布")
    tag_names: list[str] = Field(default_factory=list, description="技术标签名称列表")


class PostResponse(BaseModel):
    id: str
    author_id: str
    title: str
    content: str
    company: str
    position: str
    year: int
    interview_type: str | None
    status: str
    is_anonymous: bool
    likes_count: int
    comments_count: int
    created_at: datetime
    updated_at: datetime

    author_name: str = Field(description="作者名（匿名时显示'匿名用户'）")
    tags: list[TagResponse] = []
    is_liked: bool = Field(False, description="当前用户是否已点赞")

    model_config = {"from_attributes": True}


class PostListResponse(BaseModel):
    posts: list[PostResponse]
    total: int
    page: int
    size: int


class TagStatResponse(BaseModel):
    name: str
    count: int


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000, description="评论内容")
    is_anonymous: bool = Field(False, description="是否匿名评论")


class CommentResponse(BaseModel):
    id: str
    post_id: str
    content: str
    is_anonymous: bool
    created_at: datetime
    updated_at: datetime
    author_name: str = Field(description="作者名（匿名时显示'匿名用户'）")

    model_config = {"from_attributes": True}


class CommentListResponse(BaseModel):
    comments: list[CommentResponse]
    total: int
    page: int
    size: int


class ShareResponse(BaseModel):
    share_url: str
    message: str
