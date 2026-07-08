from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.auth import ProfileUpdateRequest
from app.utils.security import (
    create_access_token,
    hash_password,
    verify_password,
)


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_account(db: AsyncSession, account: str) -> User | None:
    """Find user by email OR username."""
    result = await db.execute(
        select(User).where(
            or_(User.email == account, User.username == account)
        )
    )
    return result.scalar_one_or_none()


async def register_by_email(
    db: AsyncSession, email: str, password: str
) -> tuple[User, str]:
    """Returns (user, access_token). Raises ValueError on conflict."""
    existing = await get_user_by_email(db, email)
    if existing:
        raise ValueError("该邮箱已被注册")

    username = email.split("@")[0]
    # If username collides, append a suffix
    if await get_user_by_username(db, username):
        import uuid
        username = f"{username}_{uuid.uuid4().hex[:6]}"

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    token = create_access_token({"sub": user.id})
    return user, token


async def register_by_username(
    db: AsyncSession, username: str, password: str
) -> tuple[User, str]:
    existing = await get_user_by_username(db, username)
    if existing:
        raise ValueError("该用户名已被注册")

    user = User(
        username=username,
        email=None,
        password_hash=hash_password(password),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    token = create_access_token({"sub": user.id})
    return user, token


async def authenticate(
    db: AsyncSession, account: str, password: str
) -> tuple[User, str]:
    """Returns (user, access_token). Raises ValueError on failure."""
    user = await get_user_by_account(db, account)
    if not user or not verify_password(password, user.password_hash):
        raise ValueError("账号或密码错误")
    if not user.is_active:
        raise ValueError("账号已被禁用")

    token = create_access_token({"sub": user.id})
    return user, token


async def update_profile(
    db: AsyncSession, user: User, data: ProfileUpdateRequest
) -> User:
    """Update user profile fields. Returns updated user."""
    update_fields = data.model_dump(exclude_unset=True)
    for key, value in update_fields.items():
        setattr(user, key, value)
    await db.flush()
    await db.refresh(user)
    return user


# ── Account Settings Services ─────────────────────────


async def update_username(
    db: AsyncSession, user_id: str, new_username: str
) -> User:
    """Update username. Raises ValueError if already taken."""
    existing = await get_user_by_username(db, new_username)
    if existing and existing.id != user_id:
        raise ValueError("该用户名已被占用")

    user = await get_user_by_id(db, user_id)
    if not user:
        raise ValueError("用户不存在")
    user.username = new_username
    await db.flush()
    await db.refresh(user)
    return user


async def update_email(
    db: AsyncSession, user_id: str, new_email: str
) -> User:
    """Update email. Raises ValueError if already taken."""
    existing = await get_user_by_email(db, new_email)
    if existing and existing.id != user_id:
        raise ValueError("该邮箱已被占用")

    user = await get_user_by_id(db, user_id)
    if not user:
        raise ValueError("用户不存在")
    user.email = new_email
    await db.flush()
    await db.refresh(user)
    return user


async def change_password(
    db: AsyncSession, user_id: str, old_password: str, new_password: str
) -> User:
    """Change password after verifying old password."""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise ValueError("用户不存在")
    if not verify_password(old_password, user.password_hash):
        raise ValueError("旧密码错误")
    user.password_hash = hash_password(new_password)
    await db.flush()
    await db.refresh(user)
    return user


async def deactivate_account(
    db: AsyncSession, user_id: str, password: str
) -> None:
    """Soft-delete account after verifying password."""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise ValueError("用户不存在")
    if not verify_password(password, user.password_hash):
        raise ValueError("密码错误")
    user.is_active = False
    await db.flush()
