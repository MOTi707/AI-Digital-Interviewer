from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.post import (
    CommentCreate,
    CommentListResponse,
    CommentResponse,
    PostCreate,
    PostListResponse,
    PostResponse,
    ShareResponse,
    TagStatResponse,
)
from app.services import post_service, comment_service
from app.services.post_service import _build_post_response
from app.services.comment_service import _build_comment_response

router = APIRouter(prefix="/api/posts", tags=["面经论坛"])
_optional_bearer = HTTPBearer(auto_error=False)


async def _optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_optional_bearer),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """可选的认证：有 token 则解析用户，无 token 返回 None"""
    if credentials is None:
        return None
    try:
        from app.utils.security import decode_access_token
        from app.services.auth import get_user_by_id

        payload = decode_access_token(credentials.credentials)
        if payload is None:
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
        user = await get_user_by_id(db, user_id)
        return user if user and user.is_active else None
    except Exception:
        return None


# ---------- 帖子 CRUD ----------


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    data: PostCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """发布面经"""
    post = await post_service.create_post(db, user, data)
    return _build_post_response(post, current_user_id=user.id, liked_post_ids=set())


@router.get("", response_model=PostListResponse)
async def list_posts(
    company: str | None = Query(None),
    position: str | None = Query(None),
    year: int | None = Query(None, ge=2020, le=2030),
    status: str | None = Query(None),
    interview_type: str | None = Query(None),
    tags: str | None = Query(None, description="逗号分隔的标签名"),
    keyword: str | None = Query(None),
    sort_by: str = Query("latest", pattern=r"^(latest|hottest)$"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user: User | None = Depends(_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """获取帖子列表（支持交叉组合筛选）"""
    tag_names = [t.strip() for t in tags.split(",") if t.strip()] if tags else None
    user_id = user.id if user else None

    posts, total = await post_service.get_posts(
        db,
        company=company,
        position=position,
        year=year,
        status=status,
        interview_type=interview_type,
        tag_names=tag_names,
        keyword=keyword,
        sort_by=sort_by,
        page=page,
        size=size,
        current_user_id=user_id,
    )

    post_ids = [p.id for p in posts]
    liked_ids = await post_service.check_user_likes(db, post_ids, user_id)

    return PostListResponse(
        posts=[_build_post_response(p, user_id, liked_ids) for p in posts],
        total=total,
        page=page,
        size=size,
    )


@router.get("/tags/stats", response_model=list[TagStatResponse])
async def tag_stats(
    limit: int = Query(30, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """获取热门标签统计"""
    return await post_service.get_tag_stats(db, limit)


@router.get("/filters/options")
async def filter_options(db: AsyncSession = Depends(get_db)):
    """获取筛选器所有可选值"""
    companies = await post_service.get_distinct_values(db, "company")
    positions = await post_service.get_distinct_values(db, "position")
    return {
        "companies": companies,
        "positions": positions,
        "statuses": ["offer", "waitlist", "rejected", "in_progress"],
        "interview_types": ["远程", "线下"],
        "years": list(range(2026, 2019, -1)),
    }


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: str,
    user: User | None = Depends(_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """获取帖子详情"""
    post = await post_service.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")

    user_id = user.id if user else None
    liked_ids = await post_service.check_user_likes(db, [post_id], user_id)
    return _build_post_response(post, user_id, liked_ids)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除帖子（仅作者可删）"""
    try:
        deleted = await post_service.delete_post(db, post_id, user.id)
        if not deleted:
            raise HTTPException(status_code=404, detail="帖子不存在")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# ---------- 点赞 ----------


@router.post("/{post_id}/like")
async def toggle_like(
    post_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """点赞/取消点赞"""
    try:
        liked = await post_service.toggle_like(db, post_id, user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"liked": liked, "message": "已点赞" if liked else "已取消点赞"}


# ---------- 评论 ----------


@router.post(
    "/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    post_id: str,
    data: CommentCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """发表评论"""
    try:
        comment = await comment_service.create_comment(db, user, post_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return _build_comment_response(comment)


@router.get("/{post_id}/comments", response_model=CommentListResponse)
async def list_comments(
    post_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """获取帖子的评论列表"""
    comments, total = await comment_service.get_comments(db, post_id, page=page, size=size)
    return CommentListResponse(
        comments=[_build_comment_response(c) for c in comments],
        total=total,
        page=page,
        size=size,
    )


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除评论（仅作者可删）"""
    try:
        deleted = await comment_service.delete_comment(db, comment_id, user.id)
        if not deleted:
            raise HTTPException(status_code=404, detail="评论不存在")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# ---------- 分享 ----------


@router.post("/{post_id}/share", response_model=ShareResponse)
async def share_post(post_id: str):
    """生成分享链接"""
    share_url = f"{_get_base_url()}/forum/post/{post_id}"
    return ShareResponse(share_url=share_url, message="分享链接已生成")


# ---------- 内部工具 ----------


def _get_base_url() -> str:
    """获取前端基础 URL"""
    return "http://localhost:5173"
