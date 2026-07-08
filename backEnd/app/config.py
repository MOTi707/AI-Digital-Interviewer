from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
    )

    # Database
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = ""
    db_password: str = ""
    db_name: str = ""

    # JWT
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24h

    # Admin
    admin_emails: str = ""

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # Deepseek API
    deepseek_api_key: str = ""
    deepseek_api_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-v4-flash"

    # iFlytek ASR
    iflytek_app_id: str = ""
    iflytek_api_key: str = ""
    iflytek_api_secret: str = ""

    # Compiler paths (optional, auto-detect from PATH if not set)
    python_bin: str | None = None
    gcc_bin: str | None = None
    gpp_bin: str | None = None
    java_bin: str | None = None
    javac_bin: str | None = None
    node_bin: str | None = None

    @property
    def database_url(self) -> str:
        return (
            f"mysql+aiomysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
            "?charset=utf8mb4"
        )

    @property
    def database_url_sync(self) -> str:
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
            "?charset=utf8mb4"
        )

    @property
    def admin_emails_list(self) -> list[str]:
        return [e.strip().lower() for e in self.admin_emails.split(",") if e.strip()]

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
