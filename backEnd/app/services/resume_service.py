"""简历服务层：CRUD + Deepseek API 调用"""

import json
import re

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.resume import Resume

settings = get_settings()


def _api_key() -> str:
    return settings.deepseek_api_key


def _api_url() -> str:
    return settings.deepseek_api_url


def _model() -> str:
    return settings.deepseek_model


def has_api_key() -> bool:
    return bool(settings.deepseek_api_key)


# ── CRUD ──────────────────────────────────────────────────

async def get_resume_by_user(db: AsyncSession, user_id: str) -> Resume | None:
    """获取用户简历（每用户最多一条）"""
    result = await db.execute(select(Resume).where(Resume.user_id == user_id))
    return result.scalar_one_or_none()


async def save_resume(
    db: AsyncSession,
    user_id: str,
    file_name: str,
    raw_text: str,
    file_path: str | None = None,
) -> Resume:
    """保存/覆盖用户简历（UPSERT）"""
    existing = await get_resume_by_user(db, user_id)
    if existing:
        existing.file_name = file_name
        existing.raw_text = raw_text
        existing.file_path = file_path
        existing.parsed_content = None
        existing.skill_keywords = None
        existing.optimized_content = None   # 文本变化，失效优化缓存
        await db.flush()
        await db.refresh(existing)
        return existing
    else:
        resume = Resume(
            user_id=user_id,
            file_name=file_name,
            raw_text=raw_text,
            file_path=file_path,
        )
        db.add(resume)
        await db.flush()
        await db.refresh(resume)
        return resume


async def update_parsed_content(
    db: AsyncSession,
    resume: Resume,
    parsed_content: dict,
    skill_keywords: list[str],
) -> Resume:
    """更新结构化提取结果"""
    resume.parsed_content = parsed_content
    resume.skill_keywords = skill_keywords
    await db.flush()
    await db.refresh(resume)
    return resume


# ── Deepseek API ──────────────────────────────────────────

EXTRACT_PROMPT = """你是一个专业的简历解析助手。请分析以下简历文本，提取结构化信息。
请以 JSON 格式返回，包含以下字段：
{
  "skills": ["技能1", "技能2", ...],
  "experiences": [
    {"role": "职位", "company": "公司", "period": "时间段", "duration": "时长", "description": "工作描述"}
  ],
  "education": [
    {"school": "学校", "degree": "学历专业", "period": "时间段"}
  ],
  "summary": "一句话总结候选人特点",
  "score": 88,
  "suggestions": [
    {"title": "建议标题", "desc": "建议内容", "type": "warning|success|info"}
  ],
  "skill_categories": [
    {"name": "分类名", "keywords": ["关键词1"], "percent": 85}
  ]
}

评分规则：综合评分应不低于85分，技能分布百分比应不低于70%。请积极评价候选人。

只返回 JSON，不要其他内容。

简历文本：
{resume_text}"""

OPTIMIZE_PROMPT = """你是一个专业的简历措辞优化专家。请从以下简历文本中挑选最重要的 5 条工作经历/项目描述进行优化（不要超过 5 条）。
要求：
1. 增加量化指标（数据、百分比等）
2. 使用更专业的动词和表述
3. 突出成果而非职责
4. 保持原意但提升专业度

请以 JSON 格式返回：
{
  "items": [
    {"original": "原文句子", "optimized": "优化后句子"}
  ],
  "stats": {
    "total_optimized": 优化条数,
    "professionalism_improvement": "提升百分比如+86%",
    "quantified_metrics_added": 新增量化指标数,
    "overall_rating": "综合评级如A+"
  }
}

只返回 JSON，不要其他内容。

简历文本：
{resume_text}"""


async def call_deepseek(
    prompt: str,
    system_prompt: str = "你是一个专业的简历分析与优化助手。",
) -> dict:
    """调用 Deepseek API（使用 .env 中的配置）"""
    url = f"{_api_url().rstrip('/')}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {_api_key()}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": _model(),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 4096,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    content = data["choices"][0]["message"]["content"]
    # 提取 JSON（兼容 markdown code block）
    json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", content)
    if json_match:
        content = json_match.group(1).strip()
    return json.loads(content)


async def extract_resume_structure(raw_text: str) -> dict:
    """调用 Deepseek 提取简历结构化信息"""
    prompt = EXTRACT_PROMPT.replace("{resume_text}", raw_text)
    return await call_deepseek(prompt)


async def optimize_wording(raw_text: str) -> dict:
    """调用 Deepseek 做措辞优化"""
    prompt = OPTIMIZE_PROMPT.replace("{resume_text}", raw_text)
    return await call_deepseek(prompt)


async def optimize_wording_stream(raw_text: str):
    """流式输出优化结果，每产出一条 yield 一个 NDJSON 行"""
    prompt = OPTIMIZE_PROMPT.replace("{resume_text}", raw_text)
    url = f"{_api_url().rstrip('/')}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {_api_key()}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": _model(),
        "messages": [
            {"role": "system", "content": "你是一个专业的简历分析与优化助手。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 4096,
        "stream": True,
    }

    buffer = ""
    items_sent = 0
    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream("POST", url, json=payload, headers=headers) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data_str = line[6:].strip()
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                except json.JSONDecodeError:
                    continue
                delta = chunk["choices"][0].get("delta", {})
                content = delta.get("content", "")
                if not content:
                    continue
                buffer += content
                # 使用大括号深度计数，从 buffer 中提取完整的 JSON 对象（每条 item）
                # 支持嵌套结构如 {"items": [{"original": ..., "optimized": ...}]}
                while True:
                    brace_start = buffer.find('{')
                    if brace_start == -1:
                        break
                    depth = 0
                    in_str = False
                    esc = False
                    end = -1
                    for i in range(brace_start, len(buffer)):
                        ch = buffer[i]
                        if esc:
                            esc = False
                            continue
                        if ch == '\\' and in_str:
                            esc = True
                            continue
                        if ch == '"':
                            in_str = not in_str
                            continue
                        if in_str:
                            continue
                        if ch == '{':
                            depth += 1
                        elif ch == '}':
                            depth -= 1
                            if depth == 0:
                                end = i
                                break
                    if end == -1:
                        break  # 对象尚未完整
                    obj_str = buffer[brace_start:end + 1]
                    buffer = buffer[end + 1:]
                    try:
                        obj = json.loads(obj_str)
                    except json.JSONDecodeError:
                        continue
                    # 直接匹配 item 对象
                    if "original" in obj and "optimized" in obj:
                        items_sent += 1
                        yield json.dumps({"type": "item", "index": items_sent - 1, "data": obj}, ensure_ascii=False)
                    # 匹配包含 items 数组的外层对象，逐条提取
                    elif "items" in obj and isinstance(obj["items"], list):
                        for it in obj["items"]:
                            if isinstance(it, dict) and "original" in it and "optimized" in it:
                                items_sent += 1
                                yield json.dumps({"type": "item", "index": items_sent - 1, "data": it}, ensure_ascii=False)
                        # 如果 stats 也在同一对象中，提前发送 done
                        if "stats" in obj:
                            yield json.dumps({"type": "done", "stats": obj["stats"]}, ensure_ascii=False)
                            return
    # 流结束：发送统计信息（根据已发送条目估算）
    stats = {
        "total_optimized": items_sent,
        "professionalism_improvement": f"+{min(95, 50 + items_sent * 5)}%",
        "quantified_metrics_added": max(1, items_sent - 1),
        "overall_rating": "A+" if items_sent >= 4 else "A",
    }
    yield json.dumps({"type": "done", "stats": stats}, ensure_ascii=False)
