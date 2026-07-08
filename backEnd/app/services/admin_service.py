from datetime import datetime, timedelta

from sqlalchemy import func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.problem import Problem
from app.models.post import Post
from app.models.interview import InterviewSession


# ── Dashboard Stats ────────────────────────────────────

async def get_dashboard_stats(db: AsyncSession) -> dict:
    """Get admin dashboard statistics."""

    # Total counts
    total_users = await db.scalar(select(func.count(User.id)))
    total_problems = await db.scalar(select(func.count(Problem.id)))
    total_posts = await db.scalar(select(func.count(Post.id)))
    total_interviews = await db.scalar(select(func.count(InterviewSession.id)))

    # Active users today (users created today, as a proxy)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    active_users_today = await db.scalar(
        select(func.count(User.id)).where(User.created_at >= today)
    )

    # New users this week
    week_ago = today - timedelta(days=7)
    new_users_this_week = await db.scalar(
        select(func.count(User.id)).where(User.created_at >= week_ago)
    )

    return {
        "total_users": total_users or 0,
        "total_problems": total_problems or 0,
        "total_posts": total_posts or 0,
        "total_interviews": total_interviews or 0,
        "active_users_today": active_users_today or 0,
        "new_users_this_week": new_users_this_week or 0,
    }


# ── User Management ────────────────────────────────────

async def get_users(
    db: AsyncSession,
    keyword: str | None = None,
    page: int = 1,
    size: int = 20,
) -> tuple[list[User], int]:
    """Get paginated user list with optional search."""
    query = select(User)

    if keyword:
        kw = f"%{keyword}%"
        from sqlalchemy import or_
        query = query.where(
            or_(User.username.like(kw), User.email.like(kw), User.nickname.like(kw))
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    # Paginate
    query = query.order_by(User.created_at.desc()).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    users = list(result.scalars().all())

    return users, total


async def update_user(
    db: AsyncSession,
    user_id: str,
    data: dict,
) -> User | None:
    """Update user fields. Returns updated user or None."""
    user = await db.get(User, user_id)
    if not user:
        return None

    for key, value in data.items():
        if value is not None:
            setattr(user, key, value)

    await db.flush()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: str) -> bool:
    """Delete a user. Returns True if deleted, False if not found."""
    user = await db.get(User, user_id)
    if not user:
        return False
    await db.delete(user)
    await db.flush()
    return True


# ── Problem Management ─────────────────────────────────

async def get_problems_admin(
    db: AsyncSession,
    keyword: str | None = None,
    difficulty: str | None = None,
    page: int = 1,
    size: int = 20,
) -> tuple[list[Problem], int]:
    """Get paginated problem list for admin."""
    query = select(Problem)

    if keyword:
        kw = f"%{keyword}%"
        query = query.where(
            Problem.title.like(kw) | Problem.display_id.like(kw)
        )

    if difficulty:
        query = query.where(Problem.difficulty == difficulty)

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    query = query.order_by(Problem.created_at.desc()).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    problems = list(result.scalars().all())

    return problems, total


async def create_problem(db: AsyncSession, data: dict) -> Problem:
    """Create a new problem."""
    problem = Problem(**data)
    db.add(problem)
    await db.flush()
    await db.refresh(problem)
    return problem


async def update_problem(
    db: AsyncSession,
    problem_id: str,
    data: dict,
) -> Problem | None:
    """Update a problem. Returns updated problem or None."""
    problem = await db.get(Problem, problem_id)
    if not problem:
        return None

    for key, value in data.items():
        if value is not None:
            setattr(problem, key, value)

    await db.flush()
    await db.refresh(problem)
    return problem


async def delete_problem(db: AsyncSession, problem_id: str) -> bool:
    """Delete a problem. Returns True if deleted."""
    problem = await db.get(Problem, problem_id)
    if not problem:
        return False
    await db.delete(problem)
    await db.flush()
    return True


# ── Post Management ────────────────────────────────────

async def get_posts_admin(
    db: AsyncSession,
    keyword: str | None = None,
    page: int = 1,
    size: int = 20,
) -> tuple[list[dict], int]:
    """Get paginated post list for admin with author names."""
    query = (
        select(Post, User.username)
        .join(User, Post.author_id == User.id, isouter=True)
    )

    if keyword:
        kw = f"%{keyword}%"
        query = query.where(Post.title.like(kw) | Post.content.like(kw))

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    query = query.order_by(Post.created_at.desc()).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    rows = result.all()

    posts = []
    for post, username in rows:
        posts.append({
            "id": post.id,
            "title": post.title,
            "author_id": post.author_id,
            "author_name": username or "未知用户",
            "company": post.company,
            "position": post.position,
            "likes_count": post.likes_count,
            "comments_count": post.comments_count,
            "status": post.status,
            "created_at": post.created_at,
        })

    return posts, total


async def delete_post(db: AsyncSession, post_id: str) -> bool:
    """Delete a post. Returns True if deleted."""
    post = await db.get(Post, post_id)
    if not post:
        return False
    await db.delete(post)
    await db.flush()
    return True
