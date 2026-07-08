from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _safe_password(plain: str) -> str:
    """bcrypt 最大支持 72 字节，超出需截断"""
    return plain.encode("utf-8")[:72].decode("utf-8", errors="ignore")


def hash_password(plain: str) -> str:
    return pwd_context.hash(_safe_password(plain))


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(_safe_password(plain), hashed)


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict | None:
    """Returns payload dict on success, None on any error."""
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        return None
