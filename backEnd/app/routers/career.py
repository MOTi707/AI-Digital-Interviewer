from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.career import (
    AssessmentListResponse,
    AssessmentQuestionsResponse,
    AssessmentResponse,
    AssessmentSubmitRequest,
    CareerRecommendRequest,
)
from app.services import career_service, resume_service

router = APIRouter(prefix="/api/career", tags=["职业测评"])


@router.get("/questions/{assessment_type}", response_model=AssessmentQuestionsResponse)
async def get_questions(assessment_type: str):
    """获取指定类型测评的题目列表（无需认证）"""
    try:
        return career_service.get_questions(assessment_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/submit",
    response_model=AssessmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_assessment(
    body: AssessmentSubmitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """提交测评答案并计算结果"""
    try:
        record = await career_service.save_assessment(
            db, current_user.id, body.type, body.answers
        )
        return AssessmentResponse(
            id=record.id,
            type=record.type,
            result=record.result,
            summary=record.summary,
            created_at=record.created_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history", response_model=AssessmentListResponse)
async def get_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户的测评历史"""
    total, records = await career_service.get_user_assessments(db, current_user.id)
    items = [
        AssessmentResponse(
            id=r.id,
            type=r.type,
            result=r.result,
            summary=r.summary,
            created_at=r.created_at,
        )
        for r in records
    ]
    return AssessmentListResponse(total=total, items=items)


@router.get("/result/{assessment_id}", response_model=AssessmentResponse)
async def get_result(
    assessment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取单个测评详情"""
    record = await career_service.get_assessment_by_id(
        db, current_user.id, assessment_id
    )
    if not record:
        raise HTTPException(status_code=404, detail="测评记录不存在")
    return AssessmentResponse(
        id=record.id,
        type=record.type,
        result=record.result,
        summary=record.summary,
        created_at=record.created_at,
    )


@router.post("/recommend/stream")
async def recommend_career_stream(
    body: CareerRecommendRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """AI 岗位匹配推荐（SSE 流式），支持缓存：有缓存直接推送，无缓存则调用 AI 并存库"""
    if not resume_service.has_api_key():
        raise HTTPException(status_code=400, detail="后端未配置 Deepseek API Key，请在 .env 中设置 DEEPSEEK_API_KEY")

    # 获取测评记录
    record = await career_service.get_assessment_by_id(
        db, current_user.id, body.assessment_id
    )
    if not record:
        raise HTTPException(status_code=404, detail="测评记录不存在")

    import json as _json

    # ── 缓存命中：直接推送缓存数据 ──
    if record.recommendation:
        cached = record.recommendation
        async def cached_stream():
            for i, job in enumerate(cached.get("jobs", [])):
                yield f"data: {_json.dumps({'type': 'job', 'index': i, 'data': job}, ensure_ascii=False)}\n\n"
            yield f"data: {_json.dumps({'type': 'done', 'prep_tips': cached.get('prep_tips', []), 'total_jobs': len(cached.get('jobs', []))}, ensure_ascii=False)}\n\n"
        return StreamingResponse(cached_stream(), media_type="text/event-stream")

    # ── 无缓存：流式生成并收集结果存库 ──
    # 获取用户简历技能（可选，失败不中断）
    skill_keywords: list[str] | None = None
    try:
        resume = await resume_service.get_resume_by_user(db, current_user.id)
        if resume and resume.skill_keywords:
            skill_keywords = resume.skill_keywords
    except Exception:
        pass

    async def event_stream():
        all_jobs = []
        final_prep_tips = []
        async for chunk in career_service.generate_career_recommendation_stream(
            test_type=record.type,
            result=record.result,
            summary=record.summary or "",
            skill_keywords=skill_keywords,
        ):
            msg = _json.loads(chunk)
            if msg.get("type") == "job":
                all_jobs.append(msg["data"])
            elif msg.get("type") == "done":
                final_prep_tips = msg.get("prep_tips", [])
            yield f"data: {chunk}\n\n"

        # 流结束后存入缓存
        try:
            record.recommendation = {"jobs": all_jobs, "prep_tips": final_prep_tips}
            await db.commit()
        except Exception:
            pass

    return StreamingResponse(event_stream(), media_type="text/event-stream")
