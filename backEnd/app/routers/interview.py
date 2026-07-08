"""模拟面试 API 路由"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.interview import InterviewAnswer
from app.schemas.interview import (
    InterviewSessionCreate,
    InterviewSessionResponse,
    QuestionListResponse,
    AnswerSubmit,
    AnswerResponse,
    AIChatRequest,
    CheatReport,
    InterviewReport,
    InterviewHistoryResponse,
    InterviewHistoryItem,
)
from app.services import interview_service

router = APIRouter(prefix="/api/interview", tags=["模拟面试"])


@router.get("/jobs", response_model=list)
async def get_jobs(user: User = Depends(get_current_user)):
    """获取岗位列表(分类)"""
    categories = interview_service.get_job_categories()
    return [c.model_dump() for c in categories]


@router.post("/start", response_model=InterviewSessionResponse, status_code=status.HTTP_201_CREATED)
async def start_interview(
    data: InterviewSessionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """开始面试(选岗位，创建session)"""
    session = await interview_service.create_session(
        db, user.id, data.job_category, data.job_title,
        interview_mode=data.interview_mode, target_round=data.target_round
    )
    return InterviewSessionResponse(
        id=session.id,
        job_category=session.job_category,
        job_title=session.job_title,
        current_round=session.current_round,
        status=session.status,
        cheat_count=session.cheat_count,
        interview_mode=session.interview_mode,
        target_round=session.target_round,
        rounds_progress=interview_service._build_rounds_progress(session.current_round, session.interview_mode, session.target_round),
        started_at=session.started_at,
    )


@router.get("/session/{session_id}", response_model=InterviewSessionResponse)
async def get_session(
    session_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取面试会话状态"""
    session = await interview_service.get_session(db, session_id, user.id)
    if not session:
        raise HTTPException(status_code=404, detail="面试会话不存在")
    return InterviewSessionResponse(
        id=session.id,
        job_category=session.job_category,
        job_title=session.job_title,
        current_round=session.current_round,
        status=session.status,
        cheat_count=session.cheat_count,
        interview_mode=session.interview_mode,
        target_round=session.target_round,
        rounds_progress=interview_service._build_rounds_progress(session.current_round, session.interview_mode, session.target_round),
        started_at=session.started_at,
    )


@router.get("/session/{session_id}/question", response_model=QuestionListResponse)
async def get_round_question(
    session_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前轮次题目"""
    session = await interview_service.get_session(db, session_id, user.id)
    if not session:
        raise HTTPException(status_code=404, detail="面试会话不存在")
    if session.status != "in_progress":
        raise HTTPException(status_code=400, detail="面试已结束")

    questions = await interview_service.get_round_questions(db, session, session.current_round)
    return QuestionListResponse(round=session.current_round, questions=questions)


@router.post("/session/{session_id}/answer", response_model=AnswerResponse)
async def submit_answer(
    session_id: str,
    data: AnswerSubmit,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """提交答案"""
    session = await interview_service.get_session(db, session_id, user.id)
    if not session:
        raise HTTPException(status_code=404, detail="面试会话不存在")
    if session.status != "in_progress":
        raise HTTPException(status_code=400, detail="面试已结束")

    result = await interview_service.grade_answer(
        db, session, data.question_id, data.answer, data.duration_seconds, session.current_round
    )
    return result


@router.post("/session/{session_id}/next", response_model=InterviewSessionResponse)
async def next_round(
    session_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """进入下一轮"""
    session = await interview_service.get_session(db, session_id, user.id)
    if not session:
        raise HTTPException(status_code=404, detail="面试会话不存在")
    if session.status != "in_progress":
        raise HTTPException(status_code=400, detail="面试已结束")

    session = await interview_service.advance_round(db, session)

    # 如果面试完成，生成报告（答题数≥3才生成）
    if session.status == "completed":
        answer_count = (await db.execute(
            select(func.count()).select_from(InterviewAnswer).where(
                InterviewAnswer.session_id == session.id
            )
        )).scalar() or 0
        if answer_count >= 3:
            await interview_service.generate_report(db, session)

    return InterviewSessionResponse(
        id=session.id,
        job_category=session.job_category,
        job_title=session.job_title,
        current_round=session.current_round,
        status=session.status,
        cheat_count=session.cheat_count,
        interview_mode=session.interview_mode,
        target_round=session.target_round,
        rounds_progress=interview_service._build_rounds_progress(session.current_round, session.interview_mode, session.target_round),
        started_at=session.started_at,
    )


@router.post("/session/{session_id}/ai-chat")
async def ai_chat(
    session_id: str,
    data: AIChatRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """AI多轮对话(SSE流式)"""
    session = await interview_service.get_session(db, session_id, user.id)
    if not session:
        raise HTTPException(status_code=404, detail="面试会话不存在")
    if session.status != "in_progress":
        raise HTTPException(status_code=400, detail="面试已结束")

    async def event_generator():
        async for chunk in interview_service.generate_ai_chat_stream(
            session, data.messages, data.round
        ):
            yield chunk

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/session/{session_id}/cheat", response_model=InterviewSessionResponse)
async def report_cheat(
    session_id: str,
    data: CheatReport,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """上报切屏事件"""
    session = await interview_service.get_session(db, session_id, user.id)
    if not session:
        raise HTTPException(status_code=404, detail="面试会话不存在")

    session = await interview_service.report_cheat(db, session, data.cheat_count)
    return InterviewSessionResponse(
        id=session.id,
        job_category=session.job_category,
        job_title=session.job_title,
        current_round=session.current_round,
        status=session.status,
        cheat_count=session.cheat_count,
        interview_mode=session.interview_mode,
        target_round=session.target_round,
        rounds_progress=interview_service._build_rounds_progress(session.current_round, session.interview_mode, session.target_round),
        started_at=session.started_at,
    )


@router.post("/session/{session_id}/abort", response_model=InterviewSessionResponse)
async def abort_interview(
    session_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """中止面试"""
    session = await interview_service.get_session(db, session_id, user.id)
    if not session:
        raise HTTPException(status_code=404, detail="面试会话不存在")

    session.status = "aborted"
    from datetime import datetime, timezone
    session.completed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(session)

    # 生成报告（答题数≥3才生成）
    answer_count = (await db.execute(
        select(func.count()).select_from(InterviewAnswer).where(
            InterviewAnswer.session_id == session.id
        )
    )).scalar() or 0
    if answer_count >= 3:
        await interview_service.generate_report(db, session)

    return InterviewSessionResponse(
        id=session.id,
        job_category=session.job_category,
        job_title=session.job_title,
        current_round=session.current_round,
        status=session.status,
        cheat_count=session.cheat_count,
        interview_mode=session.interview_mode,
        target_round=session.target_round,
        rounds_progress=interview_service._build_rounds_progress(session.current_round, session.interview_mode, session.target_round),
        started_at=session.started_at,
    )


@router.get("/session/{session_id}/report", response_model=InterviewReport)
async def get_report(
    session_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取评分报告"""
    session = await interview_service.get_session(db, session_id, user.id)
    if not session:
        raise HTTPException(status_code=404, detail="面试会话不存在")

    # 如果已有报告，直接返回
    if session.report:
        from app.schemas.interview import (
            RoundDetail, RadarData, InterviewReport as ReportSchema
        )
        r = session.report
        return ReportSchema(
            session_id=session.id,
            job_category=session.job_category,
            job_title=session.job_title,
            interview_mode=r.get("interview_mode", session.interview_mode),
            target_round=r.get("target_round", session.target_round),
            total_score=r.get("total_score", 0),
            max_total=r.get("max_total", 100),
            grade=r.get("grade", "D"),
            radar=RadarData(**r.get("radar", {"professional": 0, "logic": 0, "communication": 0, "match": 0})),
            round_details=[RoundDetail(**d) for d in r.get("round_details", [])],
            suggestions=r.get("suggestions", []),
            ai_analysis=r.get("ai_analysis", ""),
            completed_at=session.completed_at,
        )

    # 否则检查答题数是否足够
    answer_count = (await db.execute(
        select(func.count()).select_from(InterviewAnswer).where(
            InterviewAnswer.session_id == session.id
        )
    )).scalar() or 0
    if answer_count < 3:
        raise HTTPException(status_code=400, detail="答题数量不足3题，无法生成评分报告")

    # 生成新报告
    report = await interview_service.generate_report(db, session)
    return report


@router.get("/history", response_model=InterviewHistoryResponse)
async def get_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """面试历史记录"""
    total, sessions = await interview_service.get_user_sessions(db, user.id)
    return InterviewHistoryResponse(
        total=total,
        sessions=[interview_service.build_history_item(s) for s in sessions],
    )
