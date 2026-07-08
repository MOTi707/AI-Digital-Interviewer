from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.problem import (
    ProblemDetail,
    ProblemListItem,
    ProblemListResponse,
    SubmissionCreate,
    SubmissionResponse,
    UserProgressResponse,
    DebugRequest,
    DebugResponse,
)
from app.services import problem_service

router = APIRouter(prefix="/api/problems", tags=["OJ刷题"])
_optional_bearer = HTTPBearer(auto_error=False)


async def _optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_optional_bearer),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """可选的认证：有 token 则解析用户，无 token 返回 None"""
    if credentials is None:
        return None
    try:
        from app.utils.security import decode_access_token
        from app.services.auth import get_user_by_id

        payload = decode_access_token(credentials.credentials)
        if payload is None:
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
        user = await get_user_by_id(db, user_id)
        return user if user and user.is_active else None
    except Exception:
        return None


@router.get("", response_model=ProblemListResponse)
async def list_problems(
    difficulty: str | None = Query(None, pattern=r"^(easy|medium|hard)$"),
    tag: str | None = Query(None),
    keyword: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user: User | None = Depends(_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """获取题目列表（支持筛选分页）"""
    problems, total = await problem_service.get_problems(
        db,
        difficulty=difficulty,
        tag=tag,
        keyword=keyword,
        page=page,
        size=size,
        user_id=user.id if user else None,
    )

    # 检查用户已通过的题目
    user_solved_ids = set()
    if user:
        problem_ids = [p.id for p in problems]
        user_solved_ids = await problem_service.check_user_solved(
            db, user.id, problem_ids
        )

    return ProblemListResponse(
        problems=[
            problem_service.build_problem_list_item(p, user_solved_ids) for p in problems
        ],
        total=total,
        page=page,
        size=size,
    )


@router.get("/tags/options")
async def tag_options(db: AsyncSession = Depends(get_db)):
    """获取所有可选标签"""
    tags = await problem_service.get_all_tags(db)
    return {"tags": tags}


@router.get("/progress", response_model=UserProgressResponse)
async def user_progress(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取用户进度统计"""
    return await problem_service.get_user_progress(db, user.id)


@router.get("/{problem_id}", response_model=ProblemDetail)
async def get_problem(
    problem_id: str,
    user: User | None = Depends(_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """获取题目详情"""
    problem = await problem_service.get_problem(db, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="题目不存在")

    user_solved = False
    if user:
        solved_ids = await problem_service.check_user_solved(db, user.id, [problem_id])
        user_solved = problem_id in solved_ids

    return problem_service.build_problem_detail(problem, user_solved)


@router.post(
    "/{problem_id}/submit",
    response_model=SubmissionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_code(
    problem_id: str,
    data: SubmissionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """提交代码（实际执行判题）"""
    problem = await problem_service.get_problem(db, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="题目不存在")

    result = await problem_service.create_submission(
        db, user, problem, data.code, data.language
    )

    return SubmissionResponse(
        id=result.submission.id,
        problem_id=result.submission.problem_id,
        code=result.submission.code,
        language=result.submission.language,
        status=result.submission.status,
        execution_time=result.submission.execution_time,
        execution_memory=result.submission.execution_memory,
        error_detail=result.error_detail,
        created_at=result.submission.created_at,
    )


@router.post(
    "/{problem_id}/debug",
    response_model=DebugResponse,
)
async def debug_code(
    problem_id: str,
    data: DebugRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """调试代码（执行并返回输出）"""
    problem = await problem_service.get_problem(db, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="题目不存在")

    return await problem_service.debug_code(
        code=data.code,
        language=data.language,
        input_data=data.input_data,
        time_limit_ms=problem.time_limit,
    )
