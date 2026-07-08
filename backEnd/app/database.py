from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

# ── aiomysql >= 0.3 兼容性补丁 ──────────────────────────────
# aiomysql 0.3.x 的 ping() 签名变为 ping(reconnect=True)，
# 而 SQLAlchemy 的 pymysql dialect 仍调用 ping() 无参数，
# 导致 pool_pre_ping 报 TypeError。这里进行 monkey-patch。
try:
    from sqlalchemy.dialects.mysql.pymysql import MySQLDialect_pymysql
    _orig_do_ping = MySQLDialect_pymysql.do_ping
    def _patched_do_ping(self, dbapi_connection):
        try:
            dbapi_connection.ping()
        except TypeError:
            dbapi_connection.ping(reconnect=True)
    MySQLDialect_pymysql.do_ping = _patched_do_ping
except Exception:
    pass
# ─────────────────────────────────────────────────────────────

from app.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
