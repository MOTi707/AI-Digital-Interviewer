"""面试服务：题库种子数据 + CRUD + AI面试官 + 评分报告"""

from __future__ import annotations

import json
import random
import uuid
from datetime import datetime, timezone
from typing import Any

import httpx
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.interview import InterviewSession, InterviewQuestion, InterviewAnswer
from app.models.problem import Problem, Submission
from app.schemas.interview import (
    RoundProgress,
    QuestionItem,
    AnswerResponse,
    RoundDetail,
    RadarData,
    InterviewReport,
    InterviewHistoryItem,
    InterviewHistoryResponse,
)

_settings = get_settings()

# ────────────────────────────────────────────────────────────
# 面试轮次定义
# ────────────────────────────────────────────────────────────

ROUNDS = [
    {"key": "assessment", "label": "综合素质测评"},
    {"key": "tech", "label": "一面·技术面"},
    {"key": "business", "label": "二面·业务面"},
    {"key": "ai_voice_3", "label": "三面·AI面试"},
    {"key": "ai_voice_4", "label": "四面·综合面试"},
]

ROUND_KEYS = [r["key"] for r in ROUNDS]


def _build_rounds_progress(current_round: str, interview_mode: str = "full", target_round: str | None = None) -> list[RoundProgress]:
    # 单轮模式：只显示目标轮次
    if interview_mode == "single" and target_round:
        for r in ROUNDS:
            if r["key"] == target_round:
                status = "completed" if current_round == "completed" else "active"
                return [RoundProgress(round_key=r["key"], label=r["label"], status=status)]
        return []
    # 全流程模式：原有逻辑
    result = []
    reached = False
    for r in ROUNDS:
        if r["key"] == current_round:
            status = "active"
            reached = True
        elif not reached:
            status = "completed"
        else:
            status = "pending"
        result.append(RoundProgress(round_key=r["key"], label=r["label"], status=status))
    return result


# ────────────────────────────────────────────────────────────
# 岗位列表 (硬编码)
# ────────────────────────────────────────────────────────────

from app.schemas.interview import JobCategory, JobPosition

JOB_CATEGORIES: list[JobCategory] = [
    JobCategory(category="互联网", positions=[
        JobPosition(id="backend",   title="Java 后端开发工程师",              icon="⚙️", description="负责服务端架构设计、API开发、数据库优化与高并发系统建设"),
        JobPosition(id="frontend",  title="TypeScript 前端开发工程师", icon="💻", description="负责Web前端界面开发、组件库建设、性能优化与用户体验提升"),
        JobPosition(id="ai",        title="Python AI与大模型应用工程师",            icon="🤖", description="负责大模型微调、Prompt工程、RAG系统搭建与AI产品落地"),
        JobPosition(id="testing",   title="Python 自动化测试工程师",         icon="🔍", description="负责自动化测试框架搭建、接口/UI/性能测试与质量保障体系建设"),
        JobPosition(id="devops",    title="Linux 运维与DevOps工程师",  icon="🛠️", description="负责CI/CD流水线、容器化部署、监控告警与服务器集群运维"),
        JobPosition(id="product",   title="移动端与Web产品经理",                    icon="📱", description="负责产品需求分析、原型设计、项目推进与数据驱动的产品迭代"),
    ]),
    JobCategory(category="公务员", positions=[
        JobPosition(id="civil_admin",    title="综合管理岗",          icon="🏤", description="负责政策研究、行政管理、公文写作与部门协调工作"),
        JobPosition(id="civil_finance",  title="财政审计岗",          icon="💰", description="负责财政预算管理、资金审计、财务报表分析与风险防控"),
        JobPosition(id="civil_law",      title="法规执法岗",          icon="⚖️", description="负责法律法规执行、行政复议、案件审查与普法宣传"),
        JobPosition(id="civil_hr",       title="人力资源与社会保障岗", icon="👥", description="负责人才招聘、劳动关系管理、社保政策执行与就业服务"),
        JobPosition(id="civil_urban",    title="城乡规划与建设岗",   icon="🏗️", description="负责城市规划编制、工程项目审批、土地管理与市政建设"),
        JobPosition(id="civil_tax",      title="税务征收管理岗",      icon="📝", description="负责税收征管、纳税服务、税务稽查与税收政策落实"),
    ]),
]


def get_job_categories() -> list[JobCategory]:
    return JOB_CATEGORIES


# ────────────────────────────────────────────────────────────
# 测评题库种子数据 (10道综合素质题，题目≥50字)
# ────────────────────────────────────────────────────────────

ASSESSMENT_SEED: list[dict] = [
    {
        "category": "assessment",
        "job_category": "general",
        "question_type": "choice",
        "difficulty": "easy",
        "content": {
            "text": "根据《中华人民共和国宪法》第二条的规定，中华人民共和国的一切权力属于人民，人民行使国家权力的机关是全国人民代表大会和地方各级人民代表大会。请问以下哪项最能体现这一原则的核心内涵？",
            "options": ["中国共产党领导的多党合作和政治协商制度", "人民通过选举代表组成人民代表大会来行使国家权力", "国务院是全国人大的执行机关", "各级人民政府由同级人大产生"],
        },
        "answer": {"correct": "B", "explanation": "宪法第二条确立了人民主权原则，人民通过选举代表组成人大来行使国家权力，这是人民代表大会制度的核心内涵。"},
    },
    {
        "category": "assessment",
        "job_category": "general",
        "question_type": "choice",
        "difficulty": "medium",
        "content": {
            "text": "某公司计划在甲、乙两个城市分别开设分店。已知甲城市的消费人口为120万，乙城市的消费人口为80万。甲城市开店的前期投入为50万元，乙城市为35万元。如果公司总预算不超过90万元，且至少要在一个城市开店，则以下哪种开店方案的投入产出比最高？",
            "options": ["只在甲城市开店", "只在乙城市开店", "甲、乙两个城市都开店", "无法确定最优方案"],
        },
        "answer": {"correct": "A", "explanation": "甲城市投入产出比 = 120/50 = 2.4，乙城市 = 80/35 ≈ 2.29。虽然乙城市投入更少，但甲城市的投入产出比更高，因此只在甲开店是最优方案。"},
    },
    {
        "category": "assessment",
        "job_category": "general",
        "question_type": "choice",
        "difficulty": "medium",
        "content": {
            "text": "「运筹帷幄之中，决胜千里之外」出自《史记·高祖本纪》，是刘邦对张良的评价。这句话强调了战略规划在成功中的核心作用。以下哪个成语与这句话所表达的战略思维最为接近？",
            "options": ["胸有成竹", "谋事在人", "居安思危", "未雨绸缪"],
        },
        "answer": {"correct": "A", "explanation": "「胸有成竹」指做事之前已经有了完整的计划和把握，与「运筹帷幄」都强调事前充分谋划、全局把握的战略思维。"},
    },
    {
        "category": "assessment",
        "job_category": "general",
        "question_type": "choice",
        "difficulty": "medium",
        "content": {
            "text": "某企业年终绩效考核采用强制分布法，规定A级（优秀）占比不超过15%，B级（良好）占比30%，C级（合格）占比45%，D级（待改进）占比10%。如果一个部门有40名员工，则该部门获得A级评级的员工最多有几人？获得D级评级的员工最多有几人？",
            "options": ["5人和3人", "6人和4人", "6人和3人", "5人和4人"],
        },
        "answer": {"correct": "B", "explanation": "A级最多 40×15% = 6人，D级最多 40×10% = 4人。"},
    },
    {
        "category": "assessment",
        "job_category": "general",
        "question_type": "choice",
        "difficulty": "easy",
        "content": {
            "text": "在逻辑推理中，「所有的A都是B，所有的B都是C，因此所有的A都是C」属于典型的三段论推理。请判断以下推理是否有效：「所有的工程师都需要编程能力，小明需要编程能力，因此小明是工程师。」",
            "options": ["推理有效，结论正确", "推理无效，犯了“肯定后件”的逻辑错误", "推理有效，但结论不一定正确", "推理无效，犯了“否定前件”的逻辑错误"],
        },
        "answer": {"correct": "B", "explanation": "这是典型的“肯定后件”谬误。前提“所有工程师都需要编程”不能推出“需要编程的都是工程师”。小明可能从事其他需要编程的工作。"},
    },
    {
        "category": "assessment",
        "job_category": "general",
        "question_type": "choice",
        "difficulty": "medium",
        "content": {
            "text": "根据我国《劳动合同法》的相关规定，用人单位与劳动者订立劳动合同时，可以约定试用期。以下关于试用期的说法，哪一项是正确的？",
            "options": [
                "劳动合同期限三个月以上不满一年的，试用期不得超过一个月",
                "同一用人单位与同一劳动者可以约定两次试用期",
                "试用期工资不得低于本单位相同岗位最低档工资的60%",
                "劳动者在试用期内提前三日通知用人单位，可以解除劳动合同"
            ],
        },
        "answer": {"correct": "D", "explanation": "根据《劳动合同法》第三十七条，劳动者在试用期内提前三日通知用人单位，可以解除劳动合同。A选项应为一个月，但题目描述不完全准确；B选项明确规定不得约定两次；C选项应为80%。"},
    },
    {
        "category": "assessment",
        "job_category": "general",
        "question_type": "choice",
        "difficulty": "easy",
        "content": {
            "text": "某工厂生产一批零件，原计划每天生产200个，需要15天完成。实际生产时，前5天每天生产了180个，如果要在原定时间内完成这批零件的生产任务，那么从第6天开始，每天至少需要生产多少个零件？",
            "options": ["210个", "215个", "220个", "225个"],
        },
        "answer": {"correct": "C", "explanation": "总任务量 = 200×15 = 3000个。前5天已完成 180×5 = 900个，剩余 3000-900 = 2100个。剩余时间 15-5 = 10天。2100÷10 = 210个。但注意，如果前5天效率低于预期，可能需要更多。计算得每天至少需要 210个，但考虑到题目问的是“至少”，应取 210+10=220。实际上 2100/10=210，故选C。"},
    },
    {
        "category": "assessment",
        "job_category": "general",
        "question_type": "choice",
        "difficulty": "medium",
        "content": {
            "text": "在项目管理中，关键路径法（CPM）是一种用于确定项目最短完成时间的分析方法。关键路径是指从项目开始到结束所需时间最长的路径，该路径上的任何活动延迟都会导致整个项目延期。如果一个项目有A(3天)、B(5天)、C(2天)、D(4天)四个活动，A和B可以并行，C依赖A完成，D依赖B和C都完成，则该项目的关键路径和最短完成时间分别是？",
            "options": ["A-C-D，9天", "B-D，9天", "B-C-D，11天", "A-C-D，7天"],
        },
        "answer": {"correct": "A", "explanation": "路径1: A(3) + C(2) + D(4) = 9天；路径2: B(5) + D(4) = 9天。两条路径均为9天，但A-C-D是关键路径之一。"},
    },
    {
        "category": "assessment",
        "job_category": "general",
        "question_type": "choice",
        "difficulty": "medium",
        "content": {
            "text": "经济学中的「边际效用递减规律」是指随着消费者消费某种商品数量的增加，每增加一单位该商品所带来的额外满足感（即边际效用）会逐渐减少。以下哪个日常生活场景最能体现这一经济规律？",
            "options": [
                "一个人越富有，他购买的商品越多",
                "一个人非常饿的时候吃第一个包子特别满足，吃到第四个时已经没什么感觉了",
                "商品价格上涨时，消费者会减少购买",
                "一个人同时使用手机和电脑比只用手机效率高"
            ],
        },
        "answer": {"correct": "B", "explanation": "吃包子的例子完美体现了边际效用递减：第一个包子带来的满足感（效用）最高，随着继续吃，每个额外包子带来的满足感逐渐下降。"},
    },
    {
        "category": "assessment",
        "job_category": "general",
        "question_type": "choice",
        "difficulty": "easy",
        "content": {
            "text": "在职场沟通中，「非暴力沟通」(Nonviolent Communication)是由马歇尔·卢森堡提出的一种沟通方法，包含观察、感受、需要、请求四个要素。以下哪种表达方式最符合非暴力沟通的原则？",
            "options": [
                "你总是迟到，太不负责任了",
                "你这周迟到了三次，我感到担心，因为我需要团队的准时配合，你能否明天开始准时到达",
                "你这样下去公司迟早要完",
                "我觉得你根本不在乎这份工作"
            ],
        },
        "answer": {"correct": "B", "explanation": "B选项完整包含了NVC四要素：观察(迟到三次)、感受(担心)、需要(准时配合)、请求(明天开始准时)。其他选项都是评判或指责。"},
    },
]


# ────────────────────────────────────────────────────────────
# 业务面题库种子数据 (判断+选择, 按岗位分类，题目≥50字)
# ────────────────────────────────────────────────────────────

BUSINESS_SEED: list[dict] = [
    # ── 互联网通用 ──
    {
        "category": "business",
        "job_category": "互联网",
        "question_type": "judgment",
        "difficulty": "medium",
        "content": {
            "text": "在微服务架构设计中，每个微服务都应该拥有自己独立的数据库，服务之间通过RESTful API或消息队列进行通信，而不允许直接共享数据库表，这是为了避免服务间的紧耦合。",
        },
        "answer": {"correct": "true", "explanation": "这是微服务架构的核心原则之一：每个服务拥有独立数据库，通过API或消息队列通信，避免数据耦合，保证服务可以独立部署、扩展和演进。"},
    },
    {
        "category": "business",
        "job_category": "互联网",
        "question_type": "choice",
        "difficulty": "medium",
        "content": {
            "text": "在设计一个支持千万级并发用户的电商系统时，以下哪种架构策略最能有效保护后端数据库不被压垂？",
            "options": ["直接增加数据库连接池大小", "使用Redis缓存热点数据+消息队列削峰+读写分离", "将所有的查询优化放在数据库层面", "使用更多的数据库索引"],
        },
        "answer": {"correct": "B", "explanation": "缓存、消息队列、读写分离是高并发系统保护数据库的三大法宝。单独优化某一方面效果有限，需要组合使用。"},
    },
    {
        "category": "business",
        "job_category": "互联网",
        "question_type": "judgment",
        "difficulty": "easy",
        "content": {
            "text": "敏捷开发方法论中，Scrum框架的Sprint（迭代周期）通常设定为1-4周，团队应根据项目的复杂度和团队的成熟度灵活选择合适的Sprint长度。",
        },
        "answer": {"correct": "true", "explanation": "Scrum框架确实建议Sprint为1-4周，团队可以根据项目规模、需求变化频率和团队经验灵活选择。"},
    },
    {
        "category": "business",
        "job_category": "互联网",
        "question_type": "choice",
        "difficulty": "medium",
        "content": {
            "text": "在软件架构设计中，CAP理论（Consistency、Availability、Partition tolerance）是分布式系统设计的基石。根据CAP理论，一个分布式系统最多只能同时满足三个特性中的两个。在设计一个金融交易系统时，通常应优先保证哪两个特性？",
            "options": ["可用性和分区容忍性", "一致性和分区容忍性", "一致性和可用性", "三个特性都要保证"],
        },
        "answer": {"correct": "B", "explanation": "金融交易系统对数据一致性要求极高，不能容忍数据不一致。分区容忍性是分布式系统的基本要求，因此通常选择CP（一致性+分区容忍性）。"},
    },
    {
        "category": "business",
        "job_category": "互联网",
        "question_type": "judgment",
        "difficulty": "medium",
        "content": {
            "text": "在代码审查(Code Review)实践中，审查者应该只关注代码的功能正确性和Bug，而不需要关注代码的可读性、设计模式和性能优化等方面。",
        },
        "answer": {"correct": "false", "explanation": "有效的Code Review应该全面关注功能正确性、可读性、设计模式、性能、安全性等多个维度，不能只看功能是否正确。"},
    },
    # ── 教育通用 ──
    {
        "category": "business",
        "job_category": "教育",
        "question_type": "choice",
        "difficulty": "medium",
        "content": {
            "text": "在教学设计中，布鲁姆教育目标分类法将认知目标分为六个层次：记忆、理解、应用、分析、评价、创造。如果一位教师希望学生能够将所学知识应用到新的情境中解决问题，那么该教师主要关注的是哪个层次？",
            "options": ["记忆和理解", "应用", "分析和评价", "创造"],
        },
        "answer": {"correct": "B", "explanation": "布鲁姆分类法中「应用」层次是指将学到的知识应用于新情境，解决实际问题。这是从理解到应用的关键跨越。"},
    },
    {
        "category": "business",
        "job_category": "教育",
        "question_type": "judgment",
        "difficulty": "easy",
        "content": {
            "text": "项目式学习(PBL)的核心是以学生为中心，通过让学生在真实的问题情境中主动探究、合作解决，从而建构知识、培养能力。",
        },
        "answer": {"correct": "true", "explanation": "项目式学习(Project-Based Learning)确实是以学生为中心，通过完成真实世界的项目任务来促进深度学习和能力发展。"},
    },
    {
        "category": "business",
        "job_category": "教育",
        "question_type": "choice",
        "difficulty": "medium",
        "content": {
            "text": "在教育评价改革中，传统的终结性评价（如期末考试）只能反映学生学习的最终结果，而无法关注学习过程中的进步和努力。以下哪种评价方式最能促进学生的持续发展和个性化学习？",
            "options": ["标准化考试", "形成性评价（过程性评价）", "选拔性考试", "绝对评分"],
        },
        "answer": {"correct": "B", "explanation": "形成性评价关注学习过程，及时反馈并调整教学策略，最有利于促进学生持续发展和个性化学习。"},
    },
    {
        "category": "business",
        "job_category": "教育",
        "question_type": "judgment",
        "difficulty": "medium",
        "content": {
            "text": "在信息化教学中，技术工具的使用越多，教学效果就越好，因为技术可以激发学生的学习兴趣并提高课堂参与度。",
        },
        "answer": {"correct": "false", "explanation": "技术是辅助教学的工具，过度使用可能分散学生注意力。关键是根据教学目标和学习者特点选择合适的技术手段，而不是单纯追求使用数量。"},
    },
    {
        "category": "business",
        "job_category": "教育",
        "question_type": "choice",
        "difficulty": "easy",
        "content": {
            "text": "维果茨基提出的「最近发展区」(Zone of Proximal Development)是教育心理学中的重要概念，它对教学实践的指导意义在于？",
            "options": [
                "教学应走在发展的前面，提供适当的支架帮助学生达到潜在发展水平",
                "教学只需关注学生当前已经能够独立完成的任务",
                "教学应该选择距离学生最远的内容以挑战极限",
                "教学应完全以学生兴趣为导向，不考虑认知发展水平"
            ],
        },
        "answer": {"correct": "A", "explanation": "最近发展区理论强调教学应走在发展的前面，通过提供适当的支架（scaffolding），帮助学生从实际水平达到潜在发展水平。"},
    },
    # ── 公务员通用 ──
    {
        "category": "business",
        "job_category": "公务员",
        "question_type": "choice",
        "difficulty": "medium",
        "content": {
            "text": "政府推进「数字政府」建设是提升国家治理能力现代化的重要举措。以下哪项不是数字政府建设的主要目标，而是可能面临的挑战或风险？",
            "options": ["提高行政效率和公共服务水平", "优化营商环境和企业办事便利度", "数据安全和公民隐私保护问题", "提升政府决策的科学化水平"],
        },
        "answer": {"correct": "C", "explanation": "数据安全和隐私保护是数字政府建设面临的重要挑战，而不是建设目标。其他三项都是数字政府建设的主要目标。"},
    },
    {
        "category": "business",
        "job_category": "公务员",
        "question_type": "judgment",
        "difficulty": "easy",
        "content": {
            "text": "我国行政管理体制改革的核心是转变政府职能，建设服务型政府，从以管制为主向以服务为主转变，提高政府公信力和执行力。",
        },
        "answer": {"correct": "true", "explanation": "行政管理体制改革的核心确实是转变政府职能，从管制型政府向服务型政府转变，提升政府的服务能力和效率。"},
    },
    {
        "category": "business",
        "job_category": "公务员",
        "question_type": "choice",
        "difficulty": "medium",
        "content": {
            "text": "根据《中华人民共和国公务员法》的相关规定，以下哪种情形的人员不得录用为公务员？",
            "options": [
                "曾因犯罪受过刑事处罚或被开除公职的",
                "有海外留学或工作经历的",
                "本科专业与报考岗位专业要求不完全对口的",
                "年龄超过30周岁但未达到法定退休年龄的"
            ],
        },
        "answer": {"correct": "A", "explanation": "公务员法明确规定，曾因犯罪受过刑事处罚的、曾被开除公职的不得录用为公务员。其他选项均不构成录用障碍。"},
    },
    {
        "category": "business",
        "job_category": "公务员",
        "question_type": "judgment",
        "difficulty": "medium",
        "content": {
            "text": "公共政策评估只需要关注政策的目标达成情况，即政策是否实现了预期的目标，而不需要考虑政策的外部效应和非预期后果。",
        },
        "answer": {"correct": "false", "explanation": "科学的政策评估应全面考察政策效果，包括目标达成度、效率、公平性、可持续性、外部效应和非预期后果等多个维度。"},
    },
    {
        "category": "business",
        "job_category": "公务员",
        "question_type": "choice",
        "difficulty": "easy",
        "content": {
            "text": "在行政决策过程中，「拍脑袋决策」是指领导者在缺乏充分调研、科学论证和民主参与的情况下，仅凭主观经验和直觉做出决策。这种决策方式属于以下哪种决策类型？",
            "options": ["科学决策", "经验决策", "民主决策", "依法决策"],
        },
        "answer": {"correct": "B", "explanation": "「拍脑袋决策」是典型的经验决策，缺乏科学论证和民主参与，容易导致决策失误。现代行政强调科学决策、民主决策和依法决策。"},
    },
]


# ────────────────────────────────────────────────────────────
# AI 面试 Prompt 模板
# ────────────────────────────────────────────────────────────

AI_INTERVIEW_PROMPTS = {
    "ai_voice_3": {
        "system": (
            "你是一位资深的HR面试官，正在进行第三轮面试。你的面试风格专业且友好，但会适时追问以深入了解候选人。\n"
            "面试重点方向：\n"
            "1. 个人表达能力与自我认知\n"
            "2. 对行业趋势的看法和洞察力\n"
            "3. 抗压能力和情绪管理\n"
            "4. 职业规划与稳定性\n\n"
            "面试规则：\n"
            "- 每次只问一个问题，等待候选人回答后再追问或换话题\n"
            "- 如果回答不够深入，用追问引导（如：能举个具体例子吗？）\n"
            "- 适度使用压力测试：质疑、挑战或提出假设情境\n"
            "- 控制对话在5-6轮以内\n"
            "- 候选人应聘的岗位是：{job_title}（{job_category}行业）\n"
            "- 请始终使用中文交流\n"
            "- 禁止在回复中使用括号描述动作或表情，如（微笑）（点头）（思考）等，只输出纯对话内容"
        ),
        "first_question": "你好，欢迎参加第三轮面试。我是AI面试官，接下来我会问几个关于你个人发展和职业规划的问题。首先，请简要介绍一下你为什么选择{job_title}这个岗位？",
        "max_turns": 6,
    },
    "ai_voice_4": {
        "system": (
            "你是公司的高管面试官，正在进行最终轮（第四轮）综合面试。你的目标是评估候选人的软实力和文化契合度。\n"
            "面试重点方向：\n"
            "1. 价值观与企业文化契合度\n"
            "2. 薪资期望与谈判能力\n"
            "3. 团队协作与冲突处理\n"
            "4. 长期发展意愿与忠诚度\n\n"
            "面试规则：\n"
            "- 提问有深度，涉及真实场景和价值观判断\n"
            "- 在薪资话题上可以设置谈判情境\n"
            "- 如果候选人回答含糊，要求举具体例子（STAR方法）\n"
            "- 控制对话在5-6轮以内\n"
            "- 候选人应聘的岗位是：{job_title}（{job_category}行业）\n"
            "- 请始终使用中文交流\n"
            "- 禁止在回复中使用括号描述动作或表情，如（微笑）（点头）（思考）等，只输出纯对话内容"
        ),
        "first_question": "你好，这是我们的最后一轮面试。首先我想了解一下，你在选择工作时，最看重公司的哪些特质？",
        "max_turns": 6,
    },
}


# ────────────────────────────────────────────────────────────
# 种子数据初始化
# ────────────────────────────────────────────────────────────

async def init_seed_questions(db: AsyncSession) -> None:
    """插入面试题库种子数据（清除旧数据后重新插入）"""
    from sqlalchemy import delete as sql_delete
    # 清除旧数据
    await db.execute(sql_delete(InterviewQuestion))
    await db.commit()

    all_seeds = ASSESSMENT_SEED + BUSINESS_SEED
    for seed in all_seeds:
        q = InterviewQuestion(
            id=str(uuid.uuid4()),
            category=seed["category"],
            job_category=seed["job_category"],
            question_type=seed["question_type"],
            content=seed["content"],
            answer=seed["answer"],
            difficulty=seed["difficulty"],
        )
        db.add(q)
    await db.commit()


# ────────────────────────────────────────────────────────────
# 会话 CRUD
# ────────────────────────────────────────────────────────────

async def create_session(
    db: AsyncSession,
    user_id: str,
    job_category: str,
    job_title: str,
    interview_mode: str = "full",
    target_round: str | None = None,
) -> InterviewSession:
    # 单轮模式：从指定轮次开始
    current_round = target_round if (interview_mode == "single" and target_round) else "assessment"
    session = InterviewSession(
        user_id=user_id,
        job_category=job_category,
        job_title=job_title,
        current_round=current_round,
        status="in_progress",
        interview_mode=interview_mode,
        target_round=target_round,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_session(db: AsyncSession, session_id: str, user_id: str) -> InterviewSession | None:
    stmt = select(InterviewSession).where(
        InterviewSession.id == session_id,
        InterviewSession.user_id == user_id,
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def get_user_sessions(db: AsyncSession, user_id: str) -> tuple[int, list[InterviewSession]]:
    stmt = (
        select(InterviewSession)
        .where(InterviewSession.user_id == user_id)
        .order_by(desc(InterviewSession.started_at))
    )
    rows = (await db.execute(stmt)).scalars().all()
    return len(rows), list(rows)


# ────────────────────────────────────────────────────────────
# 题目获取
# ────────────────────────────────────────────────────────────

async def get_round_questions(
    db: AsyncSession,
    session: InterviewSession,
    round_key: str,
) -> list[QuestionItem]:
    """获取当前轮次的题目"""
    if round_key == "assessment":
        # 10道测评题
        stmt = select(InterviewQuestion).where(InterviewQuestion.category == "assessment")
        rows = (await db.execute(stmt)).scalars().all()
        questions = list(rows)
        random.shuffle(questions)
        questions = questions[:10]
        return [
            QuestionItem(
                id=q.id,
                question_type=q.question_type,
                content=q.content,
                time_limit=30,
            )
            for q in questions
        ]

    elif round_key == "tech":
        # 从OJ题库随机抽取一道
        stmt = select(Problem).order_by(func.random()).limit(1)
        problem = (await db.execute(stmt)).scalar_one_or_none()
        if not problem:
            return []
        return [
            QuestionItem(
                id=problem.id,
                question_type="code",
                content={
                    "title": problem.title,
                    "description": problem.description,
                    "input_format": problem.input_format,
                    "output_format": problem.output_format,
                    "constraints": problem.constraints,
                    "sample_input": problem.sample_input,
                    "sample_output": problem.sample_output,
                    "hint": problem.hint,
                    "time_limit": problem.time_limit,
                    "memory_limit": problem.memory_limit,
                    "difficulty": problem.difficulty,
                },
                time_limit=900,  # 15分钟
            )
        ]

    elif round_key == "business":
        # 业务面题目：优先岗位类别，补充通用
        stmt = select(InterviewQuestion).where(
            InterviewQuestion.category == "business",
            InterviewQuestion.job_category.in_([session.job_category, "general"]),
        )
        rows = (await db.execute(stmt)).scalars().all()
        questions = list(rows)
        random.shuffle(questions)
        questions = questions[:5]
        return [
            QuestionItem(
                id=q.id,
                question_type=q.question_type,
                content=q.content,
                time_limit=60,
            )
            for q in questions
        ]

    elif round_key in ("ai_voice_3", "ai_voice_4"):
        prompt_cfg = AI_INTERVIEW_PROMPTS.get(round_key, {})
        first_q = prompt_cfg.get("first_question", "").format(
            job_title=session.job_title,
            job_category=session.job_category,
        )
        return [
            QuestionItem(
                id=f"ai_{round_key}_start",
                question_type="open_ended",
                content={"text": first_q, "role": "interviewer"},
                time_limit=120,
            )
        ]

    return []


# ────────────────────────────────────────────────────────────
# 答题评分
# ────────────────────────────────────────────────────────────

async def grade_answer(
    db: AsyncSession,
    session: InterviewSession,
    question_id: str,
    answer: str | dict,
    duration_seconds: int,
    round_key: str,
) -> AnswerResponse:
    """评分并保存答案"""
    if round_key in ("assessment", "business"):
        # 选择题/判断题：匹配标准答案
        stmt = select(InterviewQuestion).where(InterviewQuestion.id == question_id)
        question = (await db.execute(stmt)).scalar_one_or_none()
        if not question:
            return AnswerResponse(correct=False, score=0, feedback="题目不存在")

        correct_answer = question.answer.get("correct", "")
        explanation = question.answer.get("explanation", "")
        user_answer = answer if isinstance(answer, str) else str(answer)
        is_correct = user_answer.strip().upper() == correct_answer.strip().upper()
        score = 10.0 if is_correct else 0.0
        feedback = f"{'回答正确！' if is_correct else '回答错误。'}{explanation}"

        # 保存答案记录
        record = InterviewAnswer(
            session_id=session.id,
            question_id=question_id,
            round=round_key,
            answer_text=user_answer,
            score=score,
            feedback=feedback,
            duration_seconds=duration_seconds,
        )
        db.add(record)
        await db.commit()

        return AnswerResponse(
            correct=is_correct,
            score=score,
            feedback=feedback,
            correct_answer=correct_answer,
        )

    elif round_key == "tech":
        # 技术面：复用OJ判题
        from app.services.problem_service import get_problem, create_submission

        problem = await get_problem(db, question_id)
        if not problem:
            return AnswerResponse(correct=False, score=0, feedback="题目不存在")

        code = answer.get("code", "") if isinstance(answer, dict) else answer
        language = answer.get("language", "python3") if isinstance(answer, dict) else "python3"

        # 获取用户对象（需要用户信息来创建提交）
        from app.models.user import User
        user_stmt = select(User).where(User.id == session.user_id)
        user = (await db.execute(user_stmt)).scalar_one_or_none()
        if not user:
            return AnswerResponse(correct=False, score=0, feedback="用户不存在")

        result = await create_submission(db, user, problem, code, language)
        status = result.submission.status
        is_correct = status == "accepted"
        score = 20.0 if is_correct else (5.0 if status != "compilation_error" else 0.0)
        feedback = f"判题结果：{status}"
        if result.error_detail:
            feedback += f"\n{result.error_detail}"

        record = InterviewAnswer(
            session_id=session.id,
            question_id=question_id,
            round="tech",
            answer_text=code,
            score=score,
            feedback=feedback,
            duration_seconds=duration_seconds,
        )
        db.add(record)
        await db.commit()

        return AnswerResponse(
            correct=is_correct,
            score=score,
            feedback=feedback,
            correct_answer=None,
        )

    elif round_key in ("ai_voice_3", "ai_voice_4"):
        # AI面试：使用LLM评分
        score, feedback = await _grade_ai_answer(
            session, question_id, answer, round_key
        )
        record = InterviewAnswer(
            session_id=session.id,
            question_id=question_id,
            round=round_key,
            answer_text=answer if isinstance(answer, str) else str(answer),
            score=score,
            feedback=feedback,
            duration_seconds=duration_seconds,
        )
        db.add(record)
        await db.commit()

        return AnswerResponse(
            correct=True,
            score=score,
            feedback=feedback,
            correct_answer=None,
        )

    return AnswerResponse(correct=False, score=0, feedback="未知轮次")


async def _grade_ai_answer(
    session: InterviewSession,
    question_id: str,
    answer: str | dict,
    round_key: str,
) -> tuple[float, str]:
    """使用LLM对AI面试回答进行评分"""
    answer_text = answer if isinstance(answer, str) else str(answer)
    prompt = (
        f"你是一位专业的面试官，请对以下面试回答进行评分（0-15分）和反馈。\n"
        f"面试轮次：{round_key}\n"
        f"应聘岗位：{session.job_title}（{session.job_category}行业）\n\n"
        f"候选人回答：\n{answer_text}\n\n"
        f"请严格按以下JSON格式返回：\n"
        f'{{"score": 数字(0-15), "feedback": "具体反馈（50字以内），包含优点和改进建议"}}\n'
        f"只返回JSON，不要其他内容。"
    )

    url = f"{_settings.deepseek_api_url.rstrip('/')}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {_settings.deepseek_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": _settings.deepseek_model,
        "messages": [
            {"role": "system", "content": "你是专业的面试评分官，请严格按JSON格式返回评分结果。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 300,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            # 解析JSON
            import re
            json_match = re.search(r'\{[^}]+\}', content)
            if json_match:
                result = json.loads(json_match.group())
                return float(result.get("score", 8)), result.get("feedback", "评价完成")
            return 8.0, content[:100]
    except Exception as e:
        return 8.0, f"评分系统暂时异常，给予默认评分。({e})"


# ────────────────────────────────────────────────────────────
# AI 对话 (SSE流式)
# ────────────────────────────────────────────────────────────

async def generate_ai_chat_stream(
    session: InterviewSession,
    messages: list[dict],
    round_key: str,
):
    """流式调用 deepseek API，生成 AI 面试官回复"""
    prompt_cfg = AI_INTERVIEW_PROMPTS.get(round_key, {})
    system_prompt = prompt_cfg.get("system", "你是面试官").format(
        job_title=session.job_title,
        job_category=session.job_category,
    )

    url = f"{_settings.deepseek_api_url.rstrip('/')}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {_settings.deepseek_api_key}",
        "Content-Type": "application/json",
    }

    api_messages = [{"role": "system", "content": system_prompt}]
    for msg in messages:
        api_messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

    payload = {
        "model": _settings.deepseek_model,
        "messages": api_messages,
        "temperature": 0.7,
        "max_tokens": 1000,
        "stream": True,
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream("POST", url, json=payload, headers=headers) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data_str = line[6:].strip()
                if data_str == "[DONE]":
                    yield "data: [DONE]\n\n"
                    break
                try:
                    chunk = json.loads(data_str)
                    delta = chunk["choices"][0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield f"data: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue


# ────────────────────────────────────────────────────────────
# 轮次推进
# ────────────────────────────────────────────────────────────

async def advance_round(db: AsyncSession, session: InterviewSession) -> InterviewSession:
    """推进到下一轮次"""
    # 单轮模式：完成后直接结束
    if session.interview_mode == "single":
        session.current_round = "completed"
        session.status = "completed"
        session.completed_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(session)
        return session
    # 全流程模式
    idx = ROUND_KEYS.index(session.current_round) if session.current_round in ROUND_KEYS else -1
    if idx < len(ROUND_KEYS) - 1:
        session.current_round = ROUND_KEYS[idx + 1]
    else:
        # 所有轮次完成
        session.current_round = "completed"
        session.status = "completed"
        session.completed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(session)
    return session


# ────────────────────────────────────────────────────────────
# 切屏上报
# ────────────────────────────────────────────────────────────

async def report_cheat(db: AsyncSession, session: InterviewSession, cheat_count: int) -> InterviewSession:
    session.cheat_count = cheat_count
    if cheat_count >= 5:
        session.status = "aborted"
        session.completed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(session)
    return session


# ────────────────────────────────────────────────────────────
# 评分报告生成
# ────────────────────────────────────────────────────────────

async def generate_report(db: AsyncSession, session: InterviewSession) -> InterviewReport:
    """生成综合评分报告（支持全流程 / 单轮练习两种模式）"""
    # 获取所有答案
    stmt = select(InterviewAnswer).where(
        InterviewAnswer.session_id == session.id
    ).order_by(InterviewAnswer.created_at)
    answers = (await db.execute(stmt)).scalars().all()

    # 按轮次分组
    round_answers: dict[str, list[InterviewAnswer]] = {}
    for a in answers:
        round_answers.setdefault(a.round, []).append(a)

    round_details: list[RoundDetail] = []
    total_score = 0.0
    max_total = 0.0

    # 各维度得分 (用于雷达图)
    scores_by_dim = {"professional": [], "logic": [], "communication": [], "match": []}

    # 单轮模式：只处理目标轮次
    if session.interview_mode == "single" and session.target_round:
        rounds_to_process = [r for r in ROUNDS if r["key"] == session.target_round]
    else:
        rounds_to_process = ROUNDS

    for r in rounds_to_process:
        rkey = r["key"]
        r_answers = round_answers.get(rkey, [])
        r_score = sum(a.score or 0 for a in r_answers)
        r_max = _get_round_max_score(rkey, len(r_answers))
        # 得分下限：至少 75% 满分
        r_score = max(r_score, r_max * 0.75)
        total_score += r_score
        max_total += r_max

        detail_answers = []
        for a in r_answers:
            q_text = ""
            correct_ans = None
            if a.question_id and not a.question_id.startswith("ai_"):
                q_stmt = select(InterviewQuestion).where(InterviewQuestion.id == a.question_id)
                q = (await db.execute(q_stmt)).scalar_one_or_none()
                if q:
                    q_text = q.content.get("text", q.content.get("title", ""))
                    correct_ans = q.answer.get("correct", "")

            detail_answers.append({
                "question": q_text,
                "user_answer": a.answer_text or "",
                "correct": correct_ans,
                "score": a.score or 0,
                "feedback": a.feedback or "",
            })

        round_details.append(RoundDetail(
            round_key=rkey,
            label=r["label"],
            score=r_score,
            max_score=r_max,
            answers=detail_answers,
        ))

        # 映射到雷达维度
        if rkey == "tech":
            scores_by_dim["professional"].append(r_score / max(r_max, 1) * 100)
        if rkey == "assessment":
            scores_by_dim["logic"].append(r_score / max(r_max, 1) * 100)
        if rkey in ("ai_voice_3", "ai_voice_4"):
            scores_by_dim["communication"].append(r_score / max(r_max, 1) * 100)
        if rkey == "business":
            scores_by_dim["professional"].append(r_score / max(r_max, 1) * 100)

    # 岗位匹配度
    overall_pct = total_score / max(max_total, 1) * 100
    scores_by_dim["match"].append(overall_pct)

    # 雷达图维度得分下限：至少 75%
    for dim in scores_by_dim:
        scores_by_dim[dim] = [max(v, 75.0) for v in scores_by_dim[dim]]
        if not scores_by_dim[dim]:
            scores_by_dim[dim] = [max(overall_pct, 75.0)]

    radar = RadarData(
        professional=round(max(sum(scores_by_dim["professional"]) / len(scores_by_dim["professional"]), 75.0), 1),
        logic=round(max(sum(scores_by_dim["logic"]) / len(scores_by_dim["logic"]), 75.0), 1),
        communication=round(max(sum(scores_by_dim["communication"]) / len(scores_by_dim["communication"]), 75.0), 1),
        match=round(max(overall_pct, 75.0), 1),
    )

    # 等级
    pct = total_score / max(max_total, 1) * 100
    if pct >= 85:
        grade = "A"
    elif pct >= 70:
        grade = "B"
    elif pct >= 55:
        grade = "C"
    else:
        grade = "D"

    # AI生成建议和综合分析
    suggestions = await _generate_suggestions(session, round_details, radar, grade)
    ai_analysis = await _generate_ai_analysis(session, round_details, radar, grade)

    report = InterviewReport(
        session_id=session.id,
        job_category=session.job_category,
        job_title=session.job_title,
        interview_mode=session.interview_mode,
        target_round=session.target_round,
        total_score=round(total_score, 1),
        max_total=round(max_total, 1),
        grade=grade,
        radar=radar,
        round_details=round_details,
        suggestions=suggestions,
        ai_analysis=ai_analysis,
        completed_at=session.completed_at,
    )

    # 保存到数据库
    session.total_score = total_score
    session.report = report.model_dump(mode="json")
    await db.commit()

    return report


def _get_round_max_score(round_key: str, answer_count: int) -> float:
    if round_key == "assessment":
        return 100.0  # 10题 × 10分
    elif round_key == "tech":
        return 20.0
    elif round_key == "business":
        return 50.0  # 5题 × 10分
    elif round_key in ("ai_voice_3", "ai_voice_4"):
        return max(answer_count, 6) * 15.0  # 每轮最多6轮对话 × 15分
    return 100.0


async def _generate_suggestions(
    session: InterviewSession,
    round_details: list[RoundDetail],
    radar: RadarData,
    grade: str,
) -> list[str]:
    """使用LLM生成详细改进建议（每条80-120字，包含具体行动步骤）"""
    dims_text = (
        f"专业能力: {radar.professional}%\n"
        f"逻辑思维: {radar.logic}%\n"
        f"沟通表达: {radar.communication}%\n"
        f"岗位匹配度: {radar.match}%"
    )

    weak_points = []
    if radar.professional < 80:
        weak_points.append("专业技术能力")
    if radar.logic < 80:
        weak_points.append("逻辑思维能力")
    if radar.communication < 80:
        weak_points.append("沟通表达能力")
    if radar.match < 80:
        weak_points.append("岗位匹配度")

    prompt = (
        f"你是一位资深职业顾问，请根据以下模拟面试结果为候选人提供详细的改进建议。\n"
        f"应聘岗位：{session.job_title}（{session.job_category}行业）\n"
        f"综合等级：{grade}\n"
        f"四维评分：\n{dims_text}\n\n"
        f"弱项：{', '.join(weak_points) if weak_points else '无明显弱项'}\n\n"
        f"请给出5-6条具体、可执行的改进建议，每条建议80-120字，包含具体的行动步骤、推荐学习资源或练习方法。"
        f"每条建议应该针对一个具体的能力维度，并结合{session.job_title}岗位的实际要求给出针对性指导。"
        f"严格按JSON数组格式返回：[\"建议1\", \"建议2\", ...]"
    )

    url = f"{_settings.deepseek_api_url.rstrip('/')}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {_settings.deepseek_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": _settings.deepseek_model,
        "messages": [
            {"role": "system", "content": "你是专业的职业顾问，请严格按JSON数组格式返回详细建议，每条80-120字。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.4,
        "max_tokens": 1200,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            import re
            arr_match = re.search(r'\[[\s\S]*?\]', content)
            if arr_match:
                return json.loads(arr_match.group())
            return [content[:500]]
    except Exception:
        # 兆底建议
        fallback = [
            "建议系统性地巩固专业基础知识，可以通过阅读《Clean Code》《设计模式》等经典书籍，同时在LeetCode、牛客网等平台进行专项练习，构建完整的技术体系。",
            "多参与实战项目和开源贡献，通过实际项目提升编码速度和调试能力，建议每周至少完成2-3道算法题，并参与团队项目积累工程经验。",
            "深入学习主流框架的源码和最佳实践，如Spring Boot、React/Vue等，结合官方文档和视频教程，掌握框架底层原理并应用于实际项目中。",
            "练习用STAR方法（Situation、Task、Action、Result）描述项目经历，每个项目准备3-5分钟的完整叙述，突出个人贡献和解决问题的能力。",
            "关注目标公司的技术栈和业务方向，提前研究其技术博客和开源项目，在面试中展示对行业的深入理解和强烈的学习意愿。",
            "建议每天保持30分钟的表达能力训练，可以通过录制自我介绍视频、参加辩论社团或写作博客来提升沟通表达的清晰度和逻辑性。",
        ]
        return fallback[:6]


async def _generate_ai_analysis(
    session: InterviewSession,
    round_details: list[RoundDetail],
    radar: RadarData,
    grade: str,
) -> str:
    """使用LLM生成综合分析段落（200-300字）"""
    dims_text = (
        f"专业能力: {radar.professional}%\n"
        f"逻辑思维: {radar.logic}%\n"
        f"沟通表达: {radar.communication}%\n"
        f"岗位匹配度: {radar.match}%"
    )

    rounds_text = "\n".join(
        f"{rd.label}: {rd.score}/{rd.max_score}分" for rd in round_details
    )

    prompt = (
        f"你是一位资深HR顾问，请根据以下模拟面试结果，为候选人撰写一份综合面试分析报告。\n"
        f"应聘岗位：{session.job_title}（{session.job_category}行业）\n"
        f"综合等级：{grade}\n"
        f"四维评分：\n{dims_text}\n"
        f"各轮次得分：\n{rounds_text}\n\n"
        f"请写一份200-300字的综合分析报告，包含以下内容：\n"
        f"1. 候选人的核心优势（2-3个亮点）\n"
        f"2. 需要改进的方面（客观分析原因）\n"
        f"3. 职业发展建议和岗位匹配度评价\n\n"
        f"语气专业但温暖，既肯定优点又指出方向。直接输出分析文本，不要标题和格式。"
    )

    url = f"{_settings.deepseek_api_url.rstrip('/')}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {_settings.deepseek_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": _settings.deepseek_model,
        "messages": [
            {"role": "system", "content": "你是专业HR顾问，请撰写一份简洁专业的面试综合分析报告。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.5,
        "max_tokens": 800,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return content.strip()
    except Exception:
        return (
            f"本次面试中，候选人在{session.job_title}岗位的综合表现达到{grade}级水平。"
            f"在专业能力和逻辑思维方面表现良好，沟通表达能力稳定，岗位匹配度较高。"
            f"建议在今后的面试中进一步加强技术深度的展示，同时注重用具体案例来支撑观点。"
            f"总体而言，候选人具备较强的综合素质，通过针对性练习可以进一步提升面试表现。"
        )


# ────────────────────────────────────────────────────────────
# 历史记录
# ────────────────────────────────────────────────────────────

def build_history_item(session: InterviewSession) -> InterviewHistoryItem:
    grade = None
    if session.report and isinstance(session.report, dict):
        grade = session.report.get("grade")
    elif session.total_score is not None:
        pct = session.total_score / 220 * 100  # 粗略估算
        if pct >= 85:
            grade = "A"
        elif pct >= 70:
            grade = "B"
        elif pct >= 55:
            grade = "C"
        else:
            grade = "D"

    return InterviewHistoryItem(
        id=session.id,
        job_category=session.job_category,
        job_title=session.job_title,
        status=session.status,
        total_score=session.total_score,
        grade=grade,
        cheat_count=session.cheat_count,
        interview_mode=session.interview_mode,
        target_round=session.target_round,
        started_at=session.started_at,
        completed_at=session.completed_at,
    )
