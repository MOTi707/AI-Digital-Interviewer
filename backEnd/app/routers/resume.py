import os
import uuid

import fitz  # PyMuPDF
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.resume import (
    ResumeOptimizeResponse,
    ResumeResponse,
    ResumeUploadRequest,
)
from app.services import resume_service

router = APIRouter(prefix="/api/resume", tags=["简历"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "resumes")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/config")
async def get_config(
    current_user: User = Depends(get_current_user),
):
    """获取简历模块配置（如是否配置了 API Key）"""
    return {
        "has_api_key": resume_service.has_api_key(),
    }


@router.get("/", response_model=ResumeResponse)
async def get_resume(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户的简历"""
    resume = await resume_service.get_resume_by_user(db, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="暂无简历，请先上传")
    return resume


@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    raw_text: str = Form(""),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """上传/覆盖简历原始文件 + 文本，如已配置 API Key 则自动做结构化提取"""
    print(f"[UPLOAD] file={file.filename}, raw_text_len={len(raw_text)}")
    # 保存原始文件到磁盘
    ext = os.path.splitext(file.filename or "")[1]
    saved_name = f"{current_user.id}_{uuid.uuid4().hex[:8]}{ext}"
    save_path = os.path.join(UPLOAD_DIR, saved_name)
    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)
    relative_path = os.path.join("uploads", "resumes", saved_name)

    resume = await resume_service.save_resume(
        db, current_user.id, file.filename or "", raw_text, file_path=relative_path
    )
    # 如果已配置 API Key，自动提取结构化信息
    if resume_service.has_api_key() and raw_text:
        try:
            parsed = await resume_service.extract_resume_structure(raw_text)
            skills = parsed.get("skills", [])
            await resume_service.update_parsed_content(db, resume, parsed, skills)
        except Exception:
            # AI 提取失败不影响保存
            pass
    return resume


@router.post("/analyze", response_model=ResumeResponse)
async def analyze_resume(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """手动触发 AI 结构化分析"""
    resume = await resume_service.get_resume_by_user(db, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="暂无简历")
    if not resume_service.has_api_key():
        raise HTTPException(status_code=400, detail="后端未配置 Deepseek API Key，请在 .env 中设置 DEEPSEEK_API_KEY")
    try:
        parsed = await resume_service.extract_resume_structure(resume.raw_text)
        skills = parsed.get("skills", [])
        await resume_service.update_parsed_content(db, resume, parsed, skills)
        return resume
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 分析失败：{str(e)}")


@router.post("/optimize", response_model=ResumeOptimizeResponse)
async def optimize_resume(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """AI 措辞优化（优先返回缓存，否则同步调用）"""
    if not resume_service.has_api_key():
        raise HTTPException(status_code=400, detail="后端未配置 Deepseek API Key，请在 .env 中设置 DEEPSEEK_API_KEY")

    resume = await resume_service.get_resume_by_user(db, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="暂无简历")

    # 命中缓存直接返回
    if resume.optimized_content:
        cached = resume.optimized_content
        return ResumeOptimizeResponse(
            original=cached.get("original", []),
            optimized=cached.get("optimized", []),
            stats=cached.get("stats", {}),
        )

    try:
        result = await resume_service.optimize_wording(resume.raw_text)
        items = result.get("items", [])
        stats = result.get("stats", {})
        original = [{"text": item["original"], "type": "removed"} for item in items]
        optimized = [{"text": item["optimized"], "type": "added"} for item in items]
        # 存入缓存
        resume.optimized_content = {"original": original, "optimized": optimized, "stats": stats}
        await db.commit()
        return ResumeOptimizeResponse(
            original=original,
            optimized=optimized,
            stats=stats,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 优化失败：{str(e)}")


@router.post("/optimize/stream")
async def optimize_resume_stream(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """流式 AI 措辞优化（SSE），边生成边显示。有缓存则直接推送缓存。"""
    if not resume_service.has_api_key():
        raise HTTPException(status_code=400, detail="后端未配置 Deepseek API Key")

    resume = await resume_service.get_resume_by_user(db, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="暂无简历")

    async def event_stream():
        import json
        # 立即推送 start 事件，让前端第一时间收到反馈
        yield f"data: {json.dumps({'type': 'start'}, ensure_ascii=False)}\n\n"

        # 命中缓存：直接推送缓存数据
        if resume.optimized_content:
            cached = resume.optimized_content
            for i, (orig, opt) in enumerate(zip(cached.get("original", []), cached.get("optimized", []))):
                item = {"original": orig.get("text", ""), "optimized": opt.get("text", "")}
                yield f"data: {json.dumps({'type': 'item', 'index': i, 'data': item}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'stats': cached.get('stats', {})}, ensure_ascii=False)}\n\n"
            return

        # 流式生成
        all_original = []
        all_optimized = []
        final_stats = {}
        async for chunk in resume_service.optimize_wording_stream(resume.raw_text):
            msg = json.loads(chunk)
            if msg["type"] == "item":
                item = msg["data"]
                all_original.append({"text": item["original"], "type": "removed"})
                all_optimized.append({"text": item["optimized"], "type": "added"})
            elif msg["type"] == "done":
                final_stats = msg["stats"]
            yield f"data: {chunk}\n\n"

        # 流结束后存入缓存
        try:
            resume.optimized_content = {
                "original": all_original,
                "optimized": all_optimized,
                "stats": final_stats,
            }
            await db.commit()
        except Exception:
            pass

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/extract-text")
async def extract_text_from_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """服务端提取 PDF 文本（使用 PyMuPDF，比前端 pdf.js 更可靠）"""
    content = await file.read()
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ('.pdf',):
        raise HTTPException(status_code=400, detail="仅支持 PDF 文件")
    try:
        doc = fitz.open(stream=content, filetype="pdf")
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        text = "\n\n".join(text_parts).strip()
        return {"raw_text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 文本提取失败：{str(e)}")
