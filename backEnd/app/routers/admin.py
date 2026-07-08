from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.admin import (
    AdminProblemCreate,
    AdminProblemItem,
    AdminProblemListResponse,
    AdminProblemUpdate,
    AdminPostItem,
    AdminPostListResponse,
    AdminUserItem,
    AdminUserListResponse,
    AdminUserUpdateRequest,
    DashboardStats,
)
from app.services import admin_service

router = APIRouter(prefix="/api/admin", tags=["管理后台"])


# ── Admin Guard ────────────────────────────────────────

async def _require_admin(current_user: User = Depends(get_current_user)) -> User:
    """简易管理员校验：email/username 包含 admin，或邮箱在管理员名单中"""
    settings = get_settings()
    email = (current_user.email or "").lower()
    username = (current_user.username or "").lower()
    is_admin = (
        "admin" in email
        or "admin" in username
        or email in settings.admin_emails_list
    )
    if not is_admin:
        raise HTTPException(status_code=403, detail="无管理员权限")
    return current_user


# ── Dashboard ──────────────────────────────────────────

@router.get("/stats", response_model=DashboardStats)
async def get_stats(
    _admin: User = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    """获取仪表盘统计数据"""
    return await admin_service.get_dashboard_stats(db)


# ── User Management ────────────────────────────────────

@router.get("/users", response_model=AdminUserListResponse)
async def list_users(
    keyword: str | None = Query(None, description="搜索用户名/邮箱/昵称"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    _admin: User = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    """获取用户列表（分页+搜索）"""
    users, total = await admin_service.get_users(
        db, keyword=keyword, page=page, size=size
    )
    return AdminUserListResponse(
        users=[AdminUserItem.model_validate(u) for u in users],
        total=total,
        page=page,
        size=size,
    )


@router.put("/users/{user_id}", response_model=AdminUserItem)
async def update_user(
    user_id: str,
    body: AdminUserUpdateRequest,
    _admin: User = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    """更新用户（启用/禁用等）"""
    user = await admin_service.update_user(
        db, user_id, body.model_dump(exclude_unset=True)
    )
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return AdminUserItem.model_validate(user)


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    _admin: User = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    """删除用户"""
    current_user = _admin
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己")
    deleted = await admin_service.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"message": "用户已删除"}


# ── Problem Management ─────────────────────────────────

@router.get("/problems", response_model=AdminProblemListResponse)
async def list_problems(
    keyword: str | None = Query(None, description="搜索题目/ID"),
    difficulty: str | None = Query(None, pattern=r"^(easy|medium|hard)$"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    _admin: User = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    """获取题目列表（管理端）"""
    problems, total = await admin_service.get_problems_admin(
        db, keyword=keyword, difficulty=difficulty, page=page, size=size
    )
    return AdminProblemListResponse(
        problems=[AdminProblemItem.model_validate(p) for p in problems],
        total=total,
        page=page,
        size=size,
    )


@router.post("/problems", status_code=status.HTTP_201_CREATED, response_model=AdminProblemItem)
async def create_problem(
    body: AdminProblemCreate,
    _admin: User = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    """创建题目"""
    problem = await admin_service.create_problem(db, body.model_dump())
    return AdminProblemItem.model_validate(problem)


@router.put("/problems/{problem_id}", response_model=AdminProblemItem)
async def update_problem(
    problem_id: str,
    body: AdminProblemUpdate,
    _admin: User = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    """更新题目"""
    problem = await admin_service.update_problem(
        db, problem_id, body.model_dump(exclude_unset=True)
    )
    if not problem:
        raise HTTPException(status_code=404, detail="题目不存在")
    return AdminProblemItem.model_validate(problem)


@router.delete("/problems/{problem_id}")
async def delete_problem(
    problem_id: str,
    _admin: User = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    """删除题目"""
    deleted = await admin_service.delete_problem(db, problem_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="题目不存在")
    return {"message": "题目已删除"}


# ── Post Management ────────────────────────────────────

@router.get("/posts", response_model=AdminPostListResponse)
async def list_posts(
    keyword: str | None = Query(None, description="搜索标题/内容"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    _admin: User = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    """获取帖子列表（管理端）"""
    posts, total = await admin_service.get_posts_admin(
        db, keyword=keyword, page=page, size=size
    )
    return AdminPostListResponse(
        posts=[AdminPostItem(**p) for p in posts],
        total=total,
        page=page,
        size=size,
    )


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: str,
    _admin: User = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    """删除帖子"""
    deleted = await admin_service.delete_post(db, post_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="帖子不存在")
    return {"message": "帖子已删除"}
