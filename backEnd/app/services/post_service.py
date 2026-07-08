from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import func, select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post
from app.models.like import Like
from app.models.tag import Tag, post_tags
from app.models.user import User
from app.schemas.post import PostCreate, PostResponse, TagStatResponse


async def _get_or_create_tags(db: AsyncSession, tag_names: list[str]) -> list[Tag]:
    """获取或创建标签"""
    if not tag_names:
        return []

    # 查询已有标签
    stmt = select(Tag).where(Tag.name.in_(tag_names))
    result = await db.execute(stmt)
    existing_tags = {t.name: t for t in result.scalars().all()}

    tags = []
    for name in tag_names:
        if name in existing_tags:
            tags.append(existing_tags[name])
        else:
            tag = Tag(name=name)
            db.add(tag)
            tags.append(tag)

    await db.flush()
    return tags


def _build_post_response(
    post: Post,
    current_user_id: str | None = None,
    liked_post_ids: set[str] | None = None,
) -> PostResponse:
    """将 Post ORM 对象转为 Response"""
    author_name = "匿名用户" if post.is_anonymous else (post.author.username if post.author else "未知用户")

    is_liked = False
    if liked_post_ids and post.id in liked_post_ids:
        is_liked = True

    return PostResponse(
        id=post.id,
        author_id=post.author_id,
        title=post.title,
        content=post.content,
        company=post.company,
        position=post.position,
        year=post.year,
        interview_type=post.interview_type,
        status=post.status,
        is_anonymous=post.is_anonymous,
        likes_count=post.likes_count,
        comments_count=post.comments_count,
        created_at=post.created_at,
        updated_at=post.updated_at,
        author_name=author_name,
        tags=[{"id": t.id, "name": t.name} for t in post.tags],
        is_liked=is_liked,
    )


async def create_post(
    db: AsyncSession, user: User, data: PostCreate
) -> Post:
    """创建面经帖子"""
    post = Post(
        author_id=user.id,
        title=data.title,
        content=data.content,
        company=data.company,
        position=data.position,
        year=data.year,
        interview_type=data.interview_type,
        status=data.status,
        is_anonymous=data.is_anonymous,
    )

    if data.tag_names:
        tags = await _get_or_create_tags(db, data.tag_names)
        post.tags = tags

    db.add(post)
    await db.flush()
    await db.refresh(post)
    return post


async def get_posts(
    db: AsyncSession,
    *,
    company: str | None = None,
    position: str | None = None,
    year: int | None = None,
    status: str | None = None,
    interview_type: str | None = None,
    tag_names: list[str] | None = None,
    keyword: str | None = None,
    sort_by: str = "latest",  # latest / hottest
    page: int = 1,
    size: int = 20,
    current_user_id: str | None = None,
) -> tuple[list[Post], int]:
    """获取帖子列表（支持交叉组合筛选）"""
    # 基础查询
    conditions = []

    if company:
        conditions.append(Post.company == company)
    if position:
        conditions.append(Post.position == position)
    if year:
        conditions.append(Post.year == year)
    if status:
        conditions.append(Post.status == status)
    if interview_type:
        conditions.append(Post.interview_type == interview_type)
    if keyword:
        conditions.append(
            or_(
                Post.title.ilike(f"%{keyword}%"),
                Post.content.ilike(f"%{keyword}%"),
            )
        )

    # 标签筛选：需要通过 post_tags 关联
    if tag_names:
        tag_subq = (
            select(post_tags.c.post_id)
            .join(Tag, Tag.id == post_tags.c.tag_id)
            .where(Tag.name.in_(tag_names))
            .group_by(post_tags.c.post_id)
            .having(func.count() == len(tag_names))
        )
        conditions.append(Post.id.in_(tag_subq))

    where_clause = and_(*conditions) if conditions else True

    # 总数
    count_stmt = select(func.count()).select_from(Post).where(where_clause)
    total = (await db.execute(count_stmt)).scalar_one()

    # 分页查询
    if sort_by == "hottest":
        order = [Post.likes_count.desc(), Post.created_at.desc()]
    else:
        order = [Post.created_at.desc()]

    stmt = (
        select(Post)
        .where(where_clause)
        .order_by(*order)
        .offset((page - 1) * size)
        .limit(size)
    )
    result = await db.execute(stmt)
    posts = list(result.scalars().all())

    return posts, total


async def get_post(db: AsyncSession, post_id: str) -> Post | None:
    """获取单个帖子详情"""
    stmt = select(Post).where(Post.id == post_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def delete_post(db: AsyncSession, post_id: str, user_id: str) -> bool:
    """删除帖子（仅作者可删）"""
    post = await get_post(db, post_id)
    if not post:
        return False
    if post.author_id != user_id:
        raise PermissionError("只有作者可以删除自己的帖子")

    await db.delete(post)
    await db.flush()
    return True


async def toggle_like(db: AsyncSession, post_id: str, user_id: str) -> bool:
    """切换点赞状态，返回 True 表示已点赞，False 表示取消"""
    stmt = select(Like).where(Like.post_id == post_id, Like.user_id == user_id)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    post = await get_post(db, post_id)
    if not post:
        raise ValueError("帖子不存在")

    if existing:
        await db.delete(existing)
        post.likes_count = max(0, post.likes_count - 1)
        await db.flush()
        return False
    else:
        like = Like(post_id=post_id, user_id=user_id)
        db.add(like)
        post.likes_count += 1
        await db.flush()
        return True


async def check_user_likes(
    db: AsyncSession, post_ids: list[str], user_id: str | None
) -> set[str]:
    """检查用户对一组帖子的点赞状态"""
    if not user_id or not post_ids:
        return set()

    stmt = select(Like.post_id).where(
        Like.post_id.in_(post_ids), Like.user_id == user_id
    )
    result = await db.execute(stmt)
    return set(result.scalars().all())


async def get_tag_stats(db: AsyncSession, limit: int = 30) -> list[TagStatResponse]:
    """获取热门标签及其帖子数量"""
    stmt = (
        select(Tag.name, func.count(post_tags.c.post_id).label("count"))
        .join(post_tags, Tag.id == post_tags.c.tag_id)
        .group_by(Tag.id, Tag.name)
        .order_by(func.count(post_tags.c.post_id).desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return [TagStatResponse(name=row.name, count=row.count) for row in result.all()]


async def get_distinct_values(
    db: AsyncSession, field: str
) -> list[str]:
    """获取某字段的去重值列表（用于筛选器选项）"""
    col = getattr(Post, field, None)
    if col is None:
        return []
    stmt = select(col).distinct().order_by(col)
    result = await db.execute(stmt)
    return [v for v in result.scalars().all() if v is not None]
