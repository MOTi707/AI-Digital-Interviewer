from datetime import datetime
from pydantic import BaseModel, Field


# ---------- 岗位列表 ----------

class JobPosition(BaseModel):
    id: str
    title: str
    icon: str = ""
    description: str = ""


class JobCategory(BaseModel):
    category: str
    positions: list[JobPosition]


# ---------- 面试会话 ----------

class RoundProgress(BaseModel):
    round_key: str  # assessment / tech / business / ai_voice_3 / ai_voice_4
    label: str
    status: str  # pending / active / completed


class InterviewSessionCreate(BaseModel):
    job_category: str = Field(..., min_length=1)
    job_title: str = Field(..., min_length=1)
    interview_mode: str = "full"  # full / single
    target_round: str | None = None  # 仅 single 模式


class InterviewSessionResponse(BaseModel):
    id: str
    job_category: str
    job_title: str
    current_round: str
    status: str
    cheat_count: int
    interview_mode: str = "full"
    target_round: str | None = None
    rounds_progress: list[RoundProgress]
    started_at: datetime

    model_config = {"from_attributes": True}


# ---------- 题目 ----------

class QuestionItem(BaseModel):
    id: str
    question_type: str  # choice / judgment / code / open_ended
    content: dict
    time_limit: int = 30  # 秒


class QuestionListResponse(BaseModel):
    round: str
    questions: list[QuestionItem]


# ---------- 答题 ----------

class AnswerSubmit(BaseModel):
    question_id: str = Field(..., min_length=1)
    answer: str | dict  # 选择题选项, 开放题文本, 代码题 code+language
    duration_seconds: int = 0


class AnswerResponse(BaseModel):
    correct: bool
    score: float
    feedback: str
    correct_answer: str | dict | None = None


# ---------- AI 对话 ----------

class AIChatRequest(BaseModel):
    messages: list[dict]  # [{ role, content }]
    round: str  # ai_voice_3 / ai_voice_4


class AIChatMessage(BaseModel):
    role: str
    content: str


# ---------- 切屏上报 ----------

class CheatReport(BaseModel):
    cheat_count: int


# ---------- 评分报告 ----------

class RoundDetail(BaseModel):
    round_key: str
    label: str
    score: float
    max_score: float
    answers: list[dict]  # 每题 { question, user_answer, correct, feedback }


class RadarData(BaseModel):
    professional: float  # 专业能力
    logic: float  # 逻辑思维
    communication: float  # 沟通表达
    match: float  # 岗位匹配度


class InterviewReport(BaseModel):
    session_id: str
    job_category: str
    job_title: str
    interview_mode: str = "full"
    target_round: str | None = None
    total_score: float
    max_total: float
    grade: str  # A / B / C / D
    radar: RadarData
    round_details: list[RoundDetail]
    suggestions: list[str]
    ai_analysis: str = ""
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


# ---------- 历史记录 ----------

class InterviewHistoryItem(BaseModel):
    id: str
    job_category: str
    job_title: str
    status: str
    total_score: float | None
    grade: str | None
    cheat_count: int
    interview_mode: str
    target_round: str | None
    started_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class InterviewHistoryResponse(BaseModel):
    total: int
    sessions: list[InterviewHistoryItem]
