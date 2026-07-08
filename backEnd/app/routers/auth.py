import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    DeleteAccountRequest,
    EmailRegisterRequest,
    LoginRequest,
    MessageResponse,
    ProfileUpdateRequest,
    TokenResponse,
    UpdateEmailRequest,
    UpdateUsernameRequest,
    UserResponse,
    UsernameRegisterRequest,
)
from app.services import auth as auth_service

router = APIRouter(prefix="/api/auth", tags=["认证"])

AVATAR_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "avatars")
os.makedirs(AVATAR_DIR, exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE = 5 * 1024 * 1024  # 5MB


def _build_token_response(user: User, token: str) -> TokenResponse:
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/register/email", response_model=TokenResponse, status_code=201)
async def register_email(
    body: EmailRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        user, token = await auth_service.register_by_email(
            db, body.email, body.password
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _build_token_response(user, token)


@router.post("/register/username", response_model=TokenResponse, status_code=201)
async def register_username(
    body: UsernameRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        user, token = await auth_service.register_by_username(
            db, body.username, body.password
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _build_token_response(user, token)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        user, token = await auth_service.authenticate(
            db, body.account, body.password
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    return _build_token_response(user, token)


@router.post("/logout", response_model=MessageResponse)
async def logout(_: User = Depends(get_current_user)):
    """Stateless JWT — client should discard token. This endpoint exists for API symmetry."""
    return MessageResponse(message="登出成功")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


# ── Account Settings Endpoints ─────────────────────────


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get full profile including created_at."""
    return UserResponse.model_validate(current_user)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    body: ProfileUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update profile fields."""
    try:
        user = await auth_service.update_profile(db, current_user, body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return UserResponse.model_validate(user)


@router.put("/username", response_model=TokenResponse)
async def update_username(
    body: UpdateUsernameRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        user = await auth_service.update_username(
            db, current_user.id, body.username
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    token = auth_service.create_access_token({"sub": user.id})
    return _build_token_response(user, token)


@router.put("/email", response_model=TokenResponse)
async def update_email(
    body: UpdateEmailRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        user = await auth_service.update_email(
            db, current_user.id, body.email
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    token = auth_service.create_access_token({"sub": user.id})
    return _build_token_response(user, token)


@router.put("/password", response_model=MessageResponse)
async def change_password(
    body: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        await auth_service.change_password(
            db, current_user.id, body.old_password, body.new_password
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return MessageResponse(message="密码修改成功")


@router.delete("/account", response_model=MessageResponse)
async def delete_account(
    body: DeleteAccountRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        await auth_service.deactivate_account(
            db, current_user.id, body.password
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return MessageResponse(message="账号已注销")


# ── Avatar Upload ──────────────────────────────────────


@router.post("/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload or update user avatar image."""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="仅支持 JPG / PNG / WebP / GIF 格式")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="图片大小不能超过 5MB")

    ext = os.path.splitext(file.filename or "")[1] or ".jpg"
    saved_name = f"{current_user.id}_{uuid.uuid4().hex[:8]}{ext}"
    save_path = os.path.join(AVATAR_DIR, saved_name)
    with open(save_path, "wb") as f:
        f.write(content)

    relative_path = f"uploads/avatars/{saved_name}"

    # Delete old avatar file if exists
    if current_user.avatar:
        old_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            current_user.avatar,
        )
        if os.path.isfile(old_path):
            os.remove(old_path)

    current_user.avatar = relative_path
    await db.flush()
    await db.refresh(current_user)
    return UserResponse.model_validate(current_user)
