from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User
from app.schemas.post import CommentCreate, CommentResponse


def _build_comment_response(
    comment: Comment,
) -> CommentResponse:
    """将 Comment ORM 对象转为 Response"""
    author_name = "匿名用户" if comment.is_anonymous else (
        comment.user.username if comment.user else "未知用户"
    )
    return CommentResponse(
        id=comment.id,
        post_id=comment.post_id,
        content=comment.content,
        is_anonymous=comment.is_anonymous,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        author_name=author_name,
    )


async def create_comment(
    db: AsyncSession,
    user: User,
    post_id: str,
    data: CommentCreate,
) -> Comment:
    """创建评论"""
    # 验证帖子存在
    stmt = select(Post).where(Post.id == post_id)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()
    if not post:
        raise ValueError("帖子不存在")

    comment = Comment(
        post_id=post_id,
        user_id=user.id,
        content=data.content,
        is_anonymous=data.is_anonymous,
    )
    db.add(comment)
    post.comments_count += 1
    await db.flush()
    await db.refresh(comment)
    return comment


async def get_comments(
    db: AsyncSession,
    post_id: str,
    *,
    page: int = 1,
    size: int = 20,
) -> tuple[list[Comment], int]:
    """获取帖子的评论列表"""
    # 总数
    count_stmt = select(func.count()).select_from(Comment).where(
        Comment.post_id == post_id
    )
    total = (await db.execute(count_stmt)).scalar_one()

    # 分页
    stmt = (
        select(Comment)
        .where(Comment.post_id == post_id)
        .order_by(Comment.created_at.asc())
        .offset((page - 1) * size)
        .limit(size)
    )
    result = await db.execute(stmt)
    comments = list(result.scalars().all())
    return comments, total


async def delete_comment(
    db: AsyncSession, comment_id: str, user_id: str
) -> bool:
    """删除评论（仅作者可删）"""
    stmt = select(Comment).where(Comment.id == comment_id)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()

    if not comment:
        return False
    if comment.user_id != user_id:
        raise PermissionError("只有作者可以删除自己的评论")

    # 更新帖子评论数
    stmt2 = select(Post).where(Post.id == comment.post_id)
    post_result = await db.execute(stmt2)
    post = post_result.scalar_one_or_none()
    if post:
        post.comments_count = max(0, post.comments_count - 1)

    await db.delete(comment)
    await db.flush()
    return True
