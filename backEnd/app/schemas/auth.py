import re
from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


# ── Request Schemas ──────────────────────────────────────────

class EmailRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("密码至少需要6位")
        return v


class UsernameRegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_\u4e00-\u9fa5]+$", v):
            raise ValueError("用户名只能包含字母、数字、下划线和中文")
        return v


class LoginRequest(BaseModel):
    account: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1)


# ── Response Schemas ─────────────────────────────────────────

class UserResponse(BaseModel):
    id: str
    username: str
    email: str | None = None
    nickname: str | None = None
    avatar: str | None = None
    avatar_color: str | None = None
    bio: str | None = None
    phone: str | None = None
    gender: str | None = None
    birth_date: date | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str


# ── Profile Schemas ────────────────────────────────────────

class ProfileUpdateRequest(BaseModel):
    nickname: str | None = Field(default=None, max_length=50)
    avatar_color: str | None = Field(default=None, max_length=20)
    bio: str | None = Field(default=None, max_length=500)
    phone: str | None = Field(default=None, max_length=20)
    gender: str | None = Field(default=None, max_length=10)
    birth_date: date | None = None

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str | None) -> str | None:
        if v is not None and v not in ("male", "female", "other", ""):
            raise ValueError("性别只能是 male、female 或 other")
        return v if v != "" else None


# ── Account Settings Schemas ────────────────────────────

class UpdateUsernameRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_\u4e00-\u9fa5]+$", v):
            raise ValueError("用户名只能包含字母、数字、下划线和中文")
        return v


class UpdateEmailRequest(BaseModel):
    email: EmailStr


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(min_length=1)
    new_password: str = Field(min_length=6, max_length=128)

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("密码至少需要6位")
        return v


class DeleteAccountRequest(BaseModel):
    password: str = Field(min_length=1)
