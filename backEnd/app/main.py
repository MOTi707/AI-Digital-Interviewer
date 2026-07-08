from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
import os

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import engine, Base
from app.routers.auth import router as auth_router
from app.routers.post import router as post_router
from app.routers.problem import router as problem_router
from app.routers.career import router as career_router
from app.routers.resume import router as resume_router
from app.routers.interview import router as interview_router
from app.routers.admin import router as admin_router
from app.routers.tts import router as tts_router
from app.routers.asr import router as asr_router
# 确保所有模型都被导入，create_all 才能生效
import app.models  # noqa: F401

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup: create tables if they don't exist (dev convenience)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # 初始化种子数据
    from app.database import async_session_factory
    from app.services.problem_service import init_seed_problems
    from app.services.interview_service import init_seed_questions
    async with async_session_factory() as session:
        await init_seed_problems(session)
        await init_seed_questions(session)
    yield
    # Shutdown: dispose engine
    await engine.dispose()


app = FastAPI(
    title="AI面试官 - 后端 API",
    description="AI模拟面试官系统后端服务",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router)
app.include_router(post_router)
app.include_router(problem_router)
app.include_router(career_router)
app.include_router(resume_router)
app.include_router(interview_router)
app.include_router(admin_router)
app.include_router(tts_router)
app.include_router(asr_router)

# 挂载 uploads 目录为静态文件服务
_uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(_uploads_dir, exist_ok=True)
app.mount("/api/uploads", StaticFiles(directory=_uploads_dir), name="uploads")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """自定义验证错误处理，避免二进制内容导致 UnicodeDecodeError"""
    errors = []
    for err in exc.errors():
        # 移除 input 字段，因为它可能包含二进制文件内容
        safe_err = {k: str(v) for k, v in err.items() if k != "input"}
        errors.append(safe_err)
    return JSONResponse(status_code=422, content={"detail": errors})


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
