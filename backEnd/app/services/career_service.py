"""职业测评服务：题库定义 + 评分算法 + 数据库 CRUD + AI 岗位推荐"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from typing import Any

import httpx
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.career import CareerAssessment
from app.schemas.career import (
    AnswerItem,
    AssessmentQuestionsResponse,
    QuestionItem,
    QuestionOption,
)

_settings = get_settings()

# ────────────────────────────────────────────────────────────
# 通用量表选项
# ────────────────────────────────────────────────────────────

LIKERT5_LIKE = [
    QuestionOption(label="非常不喜欢", value=1),
    QuestionOption(label="不太喜欢", value=2),
    QuestionOption(label="中立", value=3),
    QuestionOption(label="比较喜欢", value=4),
    QuestionOption(label="非常喜欢", value=5),
]

LIKERT5_AGREE = [
    QuestionOption(label="非常不同意", value=1),
    QuestionOption(label="不太同意", value=2),
    QuestionOption(label="中立", value=3),
    QuestionOption(label="比较同意", value=4),
    QuestionOption(label="非常同意", value=5),
]

LIKERT5_IMPORTANT = [
    QuestionOption(label="非常不重要", value=1),
    QuestionOption(label="不太重要", value=2),
    QuestionOption(label="一般", value=3),
    QuestionOption(label="比较重要", value=4),
    QuestionOption(label="非常重要", value=5),
]

# ────────────────────────────────────────────────────────────
# Holland RIASEC 题库（24题，每维度4题）
# 理论基础: Holland (1997) RIASEC 六边形模型
# 参考: Self-Directed Search (SDS) 活动偏好量表
#        O*NET Interest Profiler 活动偏好范式
# 量表: 5级喜好量表（1=非常不喜欢 → 5=非常喜欢）
# ────────────────────────────────────────────────────────────

HOLLAND_QUESTIONS: list[QuestionItem] = [
    # R - 现实型（Realistic）：操作、修理、户外、机械
    QuestionItem(id="holland_r1", dimension="R", text="使用扳手、螺丝刀等工具拆装和修理机械设备", options=LIKERT5_LIKE),
    QuestionItem(id="holland_r2", dimension="R", text="阅读电器或机械的操作手册并学会使用新设备", options=LIKERT5_LIKE),
    QuestionItem(id="holland_r3", dimension="R", text="在户外从事园艺、林业或农业种植等体力工作", options=LIKERT5_LIKE),
    QuestionItem(id="holland_r4", dimension="R", text="搭建模型、制作木工制品或进行金属加工", options=LIKERT5_LIKE),
    # I - 研究型（Investigative）：分析、实验、阅读、推理
    QuestionItem(id="holland_i1", dimension="I", text="设计实验方案并系统地收集和分析数据", options=LIKERT5_LIKE),
    QuestionItem(id="holland_i2", dimension="I", text="阅读学术期刊或专业书籍以深入了解某一领域", options=LIKERT5_LIKE),
    QuestionItem(id="holland_i3", dimension="I", text="运用数学模型或逻辑推理解决复杂问题", options=LIKERT5_LIKE),
    QuestionItem(id="holland_i4", dimension="I", text="对自然现象提出假设并进行验证性探索", options=LIKERT5_LIKE),
    # A - 艺术型（Artistic）：创作、设计、表演、表达
    QuestionItem(id="holland_a1", dimension="A", text="创作原创的音乐作品、诗歌或短篇小说", options=LIKERT5_LIKE),
    QuestionItem(id="holland_a2", dimension="A", text="设计具有视觉冲击力的海报、Logo 或室内空间", options=LIKERT5_LIKE),
    QuestionItem(id="holland_a3", dimension="A", text="在舞台剧中表演角色或编排舞蹈动作", options=LIKERT5_LIKE),
    QuestionItem(id="holland_a4", dimension="A", text="用摄影、绘画或数字媒体表达个人独特的审美理念", options=LIKERT5_LIKE),
    # S - 社会型（Social）：帮助、教导、咨询、关怀
    QuestionItem(id="holland_s1", dimension="S", text="为遇到困难的来访者提供心理咨询或职业指导", options=LIKERT5_LIKE),
    QuestionItem(id="holland_s2", dimension="S", text="设计课程并向学生或团队成员传授知识与技能", options=LIKERT5_LIKE),
    QuestionItem(id="holland_s3", dimension="S", text="组织和参与社区服务、支教或公益志愿活动", options=LIKERT5_LIKE),
    QuestionItem(id="holland_s4", dimension="S", text="耐心倾听他人的烦恼并给予情感上的支持和鼓励", options=LIKERT5_LIKE),
    # E - 企业型（Enterprising）：领导、推销、策划、决策
    QuestionItem(id="holland_e1", dimension="E", text="带领团队制定目标并协调资源推动项目落地", options=LIKERT5_LIKE),
    QuestionItem(id="holland_e2", dimension="E", text="向客户演示产品并通过谈判达成商业合作", options=LIKERT5_LIKE),
    QuestionItem(id="holland_e3", dimension="E", text="撰写商业计划书并分析市场机会与竞争格局", options=LIKERT5_LIKE),
    QuestionItem(id="holland_e4", dimension="E", text="在高风险高回报的情境中果断做出经营决策", options=LIKERT5_LIKE),
    # C - 常规型（Conventional）：整理、规范、报表、流程
    QuestionItem(id="holland_c1", dimension="C", text="使用电子表格对大量数据进行分类、汇总和核对", options=LIKERT5_LIKE),
    QuestionItem(id="holland_c2", dimension="C", text="按照标准操作规程（SOP）逐步完成工作任务", options=LIKERT5_LIKE),
    QuestionItem(id="holland_c3", dimension="C", text="编制财务报表、审计记录或详细的进度报告", options=LIKERT5_LIKE),
    QuestionItem(id="holland_c4", dimension="C", text="制定日程安排并严格按照时间节点推进工作", options=LIKERT5_LIKE),
]

# ────────────────────────────────────────────────────────────
# MBTI 题库（24题，每维度6题）
# 维度：EI（外向/内向）、SN（感觉/直觉）、TF（思考/情感）、JP（判断/知觉）
# score: 1-2 偏向左侧字母(E/S/T/J)，4-5 偏向右侧字母(I/N/F/P)，3=中立
# ────────────────────────────────────────────────────────────

MBTI_QUESTIONS: list[QuestionItem] = [
    # ─── E/I 维度（6题，含正向3+反向3）───
    # 理论基础: Jung 心理类型理论 / IPIP-MBTI 量表
    # 覆盖: 社交能量、独处偏好、思考-表达模式
    # 正向（低分→E，高分→I）
    QuestionItem(id="mbti_ei1", dimension="EI", text="在社交场合中，我会主动与陌生人攀谈并享受交谈过程", options=LIKERT5_AGREE),
    QuestionItem(id="mbti_ei2", dimension="EI", text="和很多人在一起会让我精力充沛、充满动力", options=LIKERT5_AGREE),
    QuestionItem(id="mbti_ei3", dimension="EI", text="我喜欢成为团队中的发言中心，乐于表达观点", options=LIKERT5_AGREE),
    # 反向（低分→E，高分→I）
    QuestionItem(id="mbti_ei4", dimension="EI", text="我更喜欢在安静的环境中独自思考而不是参加社交活动", options=LIKERT5_AGREE),
    QuestionItem(id="mbti_ei5", dimension="EI", text="我需要先在心里充分思考后才会表达想法", options=LIKERT5_AGREE),
    QuestionItem(id="mbti_ei6", dimension="EI", text="长时间社交后，我需要独处才能恢复精力", options=LIKERT5_AGREE),
    # ─── S/N 维度（6题，含正向3+反向3）───
    # 覆盖: 具体vs抽象、经验vs直觉、实用vs理论
    # 正向（低分→S，高分→N）
    QuestionItem(id="mbti_sn1", dimension="SN", text="我更关注具体可观察的事实和数据而非抽象概念", options=LIKERT5_AGREE),
    QuestionItem(id="mbti_sn2", dimension="SN", text="我倾向于依赖亲身经验和已知事实来做判断", options=LIKERT5_AGREE),
    QuestionItem(id="mbti_sn3", dimension="SN", text="我更喜欢实用的、能立即应用的知识而非纯理论", options=LIKERT5_AGREE),
    # 反向（低分→S，高分→N）
    QuestionItem(id="mbti_sn4", dimension="SN", text="我喜欢探索事物背后的深层含义和隐藏的规律", options=LIKERT5_AGREE),
    QuestionItem(id="mbti_sn5", dimension="SN", text="我经常想象未来的各种可能性和发展趋势", options=LIKERT5_AGREE),
    QuestionItem(id="mbti_sn6", dimension="SN", text="我常有突破常规的想法和联想", options=LIKERT5_AGREE),
    # ─── T/F 维度（6题，含正向3+反向3）───
    # 覆盖: 逻辑vs共情、公正vs人情、客观vs主观
    # 正向（低分→T，高分→F）
    QuestionItem(id="mbti_tf1", dimension="TF", text="做决定时，我更看重客观逻辑和证据而非个人感受", options=LIKERT5_AGREE),
    QuestionItem(id="mbti_tf2", dimension="TF", text="我认为公平公正比照顾每个人的情绪更重要", options=LIKERT5_AGREE),
    QuestionItem(id="mbti_tf3", dimension="TF", text="我更倾向于客观分析而不是凭直觉或感觉判断", options=LIKERT5_AGREE),
    # 反向（低分→T，高分→F）
    QuestionItem(id="mbti_tf4", dimension="TF", text="我很容易被他人的情绪所感染并因此改变立场", options=LIKERT5_AGREE),
    QuestionItem(id="mbti_tf5", dimension="TF", text="我经常会考虑自己的决定会如何影响他人的感受", options=LIKERT5_AGREE),
    QuestionItem(id="mbti_tf6", dimension="TF", text="当别人倾诉困难时，我更倾向于先给予情感支持而非解决方案", options=LIKERT5_AGREE),
    # ─── J/P 维度（6题，含正向3+反向3）───
    # 覆盖: 计划vs灵活、结构vs开放、确定vs探索
    # 正向（低分→J，高分→P）
    QuestionItem(id="mbti_jp1", dimension="JP", text="我喜欢提前制定详细的计划并严格按照计划执行", options=LIKERT5_AGREE),
    QuestionItem(id="mbti_jp2", dimension="JP", text="任务未完成时我会感到不安，必须先做完再休息", options=LIKERT5_AGREE),
    QuestionItem(id="mbti_jp3", dimension="JP", text="我喜欢事情有明确的结论和清晰的截止期限", options=LIKERT5_AGREE),
    # 反向（低分→J，高分→P）
    QuestionItem(id="mbti_jp4", dimension="JP", text="我更喜欢根据情况灵活调整而不是严格执行计划", options=LIKERT5_AGREE),
    QuestionItem(id="mbti_jp5", dimension="JP", text="我经常在截止日期临近时才能激发出最大的工作效率", options=LIKERT5_AGREE),
    QuestionItem(id="mbti_jp6", dimension="JP", text="我更喜欢保持选择的开放性而不是过早做出决定", options=LIKERT5_AGREE),
]

# ────────────────────────────────────────────────────────────
# 职业价值观题库（24题，6维度每维度严格4题）
# 理论基础: Super (1970) 工作价值观量表 (WVI)
#           Schwartz 价值观理论
#           Dawis & Lofquist 工作适应理论
# 维度: achievement, compensation, independence,
#        altruism, relationships, lifestyle
# 量表: 5级重要性量表（1=非常不重要 → 5=非常重要）
# ────────────────────────────────────────────────────────────

CAREER_VALUES_QUESTIONS: list[QuestionItem] = [
    # achievement 成就感 (4题) —— 追求目标达成、获得认可、不断超越
    QuestionItem(id="cv_ach1", dimension="achievement", text="工作能带来明显的成果和可见的成就感", options=LIKERT5_IMPORTANT),
    QuestionItem(id="cv_ach2", dimension="achievement", text="能够不断挑战自我、设定并超越更高目标", options=LIKERT5_IMPORTANT),
    QuestionItem(id="cv_ach3", dimension="achievement", text="工作成果能得到同事和上级的认可与赞赏", options=LIKERT5_IMPORTANT),
    QuestionItem(id="cv_ach4", dimension="achievement", text="有清晰的职业晋升路径和发展空间", options=LIKERT5_IMPORTANT),
    # compensation 经济报酬 (4题) —— 重视薪资福利和物质回报
    QuestionItem(id="cv_rew1", dimension="compensation", text="获得与工作付出相匹配的薪资报酬", options=LIKERT5_IMPORTANT),
    QuestionItem(id="cv_rew2", dimension="compensation", text="享有完善的福利待遇（保险、补贴、带薪休假等）", options=LIKERT5_IMPORTANT),
    QuestionItem(id="cv_rew3", dimension="compensation", text="有年终奖或绩效奖金等激励机制", options=LIKERT5_IMPORTANT),
    QuestionItem(id="cv_rew4", dimension="compensation", text="有股票期权、利润分享等长期财务回报", options=LIKERT5_IMPORTANT),
    # independence 自主性 (4题) —— 追求工作自由度和独立决策权
    QuestionItem(id="cv_aut1", dimension="independence", text="能够自主安排工作时间和节奏", options=LIKERT5_IMPORTANT),
    QuestionItem(id="cv_aut2", dimension="independence", text="有权决定自己的工作方式和方法", options=LIKERT5_IMPORTANT),
    QuestionItem(id="cv_aut3", dimension="independence", text="工作中能独立做决策而无需层层审批", options=LIKERT5_IMPORTANT),
    QuestionItem(id="cv_aut4", dimension="independence", text="能够自由选择和决定自己的工作内容方向", options=LIKERT5_IMPORTANT),
    # altruism 社会贡献 (4题) —— 希望通过工作为社会和他人带来价值
    QuestionItem(id="cv_con1", dimension="altruism", text="工作能为社会或他人带来积极的影响", options=LIKERT5_IMPORTANT),
    QuestionItem(id="cv_con2", dimension="altruism", text="所做的事情对世界有意义和价值", options=LIKERT5_IMPORTANT),
    QuestionItem(id="cv_con3", dimension="altruism", text="能够帮助到需要帮助的人", options=LIKERT5_IMPORTANT),
    QuestionItem(id="cv_con4", dimension="altruism", text="工作内容符合自己的价值观和道德准则", options=LIKERT5_IMPORTANT),
    # relationships 人际关系 (4题) —— 重视团队氛围和上下级关系
    QuestionItem(id="cv_rel1", dimension="relationships", text="与同事之间有良好的合作关系和信任基础", options=LIKERT5_IMPORTANT),
    QuestionItem(id="cv_rel2", dimension="relationships", text="上司尊重下属、善于沟通和给予指导", options=LIKERT5_IMPORTANT),
    QuestionItem(id="cv_rel3", dimension="relationships", text="团队氛围和谐、相互支持而非内部竞争", options=LIKERT5_IMPORTANT),
    QuestionItem(id="cv_rel4", dimension="relationships", text="有良好的人际网络和职业社交圈", options=LIKERT5_IMPORTANT),
    # lifestyle 工作环境 (4题) —— 关注工作场所舒适度与工作生活平衡
    QuestionItem(id="cv_env1", dimension="lifestyle", text="工作环境舒适、设施齐全、地理位置便利", options=LIKERT5_IMPORTANT),
    QuestionItem(id="cv_env2", dimension="lifestyle", text="有合理的工作与生活平衡，不以牺牲个人生活为代价", options=LIKERT5_IMPORTANT),
    QuestionItem(id="cv_env3", dimension="lifestyle", text="工作压力在可承受范围内，有心理安全感", options=LIKERT5_IMPORTANT),
    QuestionItem(id="cv_env4", dimension="lifestyle", text="有弹性工作制或远程办公的选择", options=LIKERT5_IMPORTANT),
]

# ────────────────────────────────────────────────────────────
# 题库元信息
# ────────────────────────────────────────────────────────────

ASSESSMENT_META = {
    "holland": {
        "title": "Holland 六维度职业兴趣测评",
        "description": "基于 Holland RIASEC 理论，探索你的职业兴趣方向（现实型R、研究型I、艺术型A、社会型S、企业型E、常规型C）",
        "questions": HOLLAND_QUESTIONS,
    },
    "mbti": {
        "title": "MBTI 性格类型测评",
        "description": "基于 Myers-Briggs 类型指标，了解你的性格倾向与沟通风格（E/I、S/N、T/F、J/P 四个维度）",
        "questions": MBTI_QUESTIONS,
    },
    "career_values": {
        "title": "职业价值观测评",
        "description": "基于 Super 工作价值观理论，探索你最看重的职业价值维度：成就感、经济报酬、自主性、社会贡献、人际关系、工作环境",
        "questions": CAREER_VALUES_QUESTIONS,
    },
}

# ────────────────────────────────────────────────────────────
# Holland 类型描述与职业推荐
# ────────────────────────────────────────────────────────────

HOLLAND_TYPE_DESC = {
    "R": {
        "name": "现实型 (Realistic)",
        "desc": "偏好使用工具、操作机械和进行体力活动，注重动手能力和实际操作技能，倾向于与物打交道而非与人交往",
        "careers": ["机械工程师", "土木工程师", "电气技术员", "农业技术专家", "飞机机械师", "木工/家具设计师", "园林景观设计", "消防工程技术"],
    },
    "I": {
        "name": "研究型 (Investigative)",
        "desc": "偏好观察、分析、推理和解决复杂问题，注重科学探究精神和逻辑思维能力，享受智力上的挑战",
        "careers": ["数据科学家", "生物医学研究员", "软件架构师", "心理学研究员", "经济分析师", "化学工程师", "天体物理学家", "人工智能研究员"],
    },
    "A": {
        "name": "艺术型 (Artistic)",
        "desc": "偏好自由、非结构化的创造性活动，注重审美感受和原创表达，善于通过艺术媒介传达情感与思想",
        "careers": ["平面设计师", "UI/UX设计师", "作家/编剧", "音乐制作人", "建筑设计师", "影视导演", "广告创意总监", "插画师"],
    },
    "S": {
        "name": "社会型 (Social)",
        "desc": "偏好与人合作，通过教育、培训、咨询和护理等方式帮助他人发展，具有强烈的社会责任感和共情能力",
        "careers": ["心理咨询师", "高校教师", "社会工作者", "人力资源经理", "职业康复师", "公共卫生专员", "非营利组织管理", "特殊教育教师"],
    },
    "E": {
        "name": "企业型 (Enterprising)",
        "desc": "偏好领导、影响和说服他人，善于组织协调和承担风险，追求经济目标和社会影响力",
        "careers": ["企业管理顾问", "投资银行家", "市场营销总监", "律师事务所合伙人", "产品经理", "政府关系经理", "创业公司CEO", "商业地产经纪"],
    },
    "C": {
        "name": "常规型 (Conventional)",
        "desc": "偏好有序、规范和数据密集型工作，注重精确性、条理性和系统性，善于在明确的规则框架内高效执行",
        "careers": ["注册会计师(CPA)", "财务分析师", "审计师", "行政管理", "数据库管理员", "质量控制工程师", "税务专员", "档案管理专家"],
    },
}

# Holland 六边形邻接关系（用于计算一致性指数）
# R-I-A-S-E-C 按六边形顺序排列，相邻维度一致性最高
HOLLAND_HEXAGON_ORDER = ["R", "I", "A", "S", "E", "C"]

# ────────────────────────────────────────────────────────────
# MBTI 类型描述
# ────────────────────────────────────────────────────────────

MBTI_TYPE_DESC = {
    "INTJ": {"name": "策略家", "desc": "富有想象力和战略性的思想家，善于将理论转化为长远的行动计划，追求效率和卓越", "strengths": ["战略思维", "独立自主", "高标准", "求知欲强", "意志坚定"], "careers": ["软件架构师", "投资分析师", "科研工作者", "战略咨询顾问", "系统分析师"], "cognitive_functions": "Ni-Te-Fi-Se"},
    "INTP": {"name": "逻辑学家", "desc": "富有创造力的发明家，对知识有着止不住的渴望，善于发现逻辑中的规律和矛盾", "strengths": ["逻辑分析", "创造力", "客观性", "适应力强", "求知欲"], "careers": ["软件开发工程师", "数学家", "哲学家", "数据科学家", "技术研究员"], "cognitive_functions": "Ti-Ne-Si-Fe"},
    "ENTJ": {"name": "指挥官", "desc": "大胆、富有想象力且意志坚强的领导者，善于制定战略并组织人力实现目标", "strengths": ["领导力", "高效", "自信", "战略眼光", "果断"], "careers": ["CEO/创业者", "管理咨询顾问", "律师", "产品经理", "企业战略规划"], "cognitive_functions": "Te-Ni-Se-Fi"},
    "ENTP": {"name": "辩论家", "desc": "聪明好奇的思想者，不会放弃任何智力上的挑战，善于在讨论中激发新想法", "strengths": ["创新", "适应力强", "有魅力", "博学", "思辨能力"], "careers": ["创业者/连续创业", "产品经理", "广告创意总监", "营销策划专家", "风险投资人"], "cognitive_functions": "Ne-Ti-Fe-Si"},
    "INFJ": {"name": "提倡者", "desc": "安静而神秘，同时鼓舞人心且不知疲倦的理想主义者，善于洞察他人的内在需求", "strengths": ["有远见", "利他主义", "有原则", "有激情", "洞察力"], "careers": ["心理咨询师", "作家/编辑", "人力资源发展", "UX设计师", "非营利组织领导"], "cognitive_functions": "Ni-Fe-Ti-Se"},
    "INFP": {"name": "调停者", "desc": "诗意、善良的利他主义者，总是热心地为正义事业提供帮助，追求内心价值观的统一", "strengths": ["理想主义", "共情力", "创造力", "开放心态", "价值观坚定"], "careers": ["作家/诗人", "心理咨询师", "社会工作者", "艺术治疗师", "内容策划"], "cognitive_functions": "Fi-Ne-Si-Te"},
    "ENFJ": {"name": "主人公", "desc": "富有魅力鼓舞人心的领导者，能够吸引听众并引导他人发挥潜能", "strengths": ["领导力", "利他主义", "有魅力", "可靠", "组织能力"], "careers": ["培训师/教练", "公关经理", "高校教师", "非营利组织领导", "人力资源总监"], "cognitive_functions": "Fe-Ni-Se-Ti"},
    "ENFP": {"name": "竞选者", "desc": "热情、有创造力、善于社交的自由精灵，能够在任何事物中找到灵感和可能性", "strengths": ["热情", "创造力", "社交能力", "乐观", "共情力"], "careers": ["记者/媒体人", "演员", "活动策划", "品牌经理", "创业顾问"], "cognitive_functions": "Ne-Fi-Te-Si"},
    "ISTJ": {"name": "物流师", "desc": "务实且注重事实的个人，可靠性不容怀疑，善于建立和维护有序的系统", "strengths": ["负责", "耐心", "诚实", "系统化", "条理性"], "careers": ["注册会计师", "项目管理专家", "质量管理工程师", "系统管理员", "审计师"], "cognitive_functions": "Si-Te-Fi-Ne"},
    "ISFJ": {"name": "守卫者", "desc": "非常专注而温暖的守护者，时刻准备着保护所爱的人，善于关注他人的具体需求", "strengths": ["支持性", "可靠", "耐心", "观察力", "责任心"], "careers": ["护士/医疗专业", "小学教师", "社会工作者", "行政助理", "客户服务经理"], "cognitive_functions": "Si-Fe-Ti-Ne"},
    "ESTJ": {"name": "总经理", "desc": "出色的管理者，在管理事物或人的方面无与伦比，善于建立规范和执行流程", "strengths": ["组织能力", "忠诚", "奉献", "诚实直接", "执行力"], "careers": ["项目经理", "法官/法律顾问", "银行经理", "供应链管理", "运营管理"], "cognitive_functions": "Te-Si-Ne-Fi"},
    "ESFJ": {"name": "执政官", "desc": "极有同情心、爱社交、受欢迎的人，总是热心助人，善于维护和谱的人际关系", "strengths": ["社交能力", "利他主义", "忠诚", "实用", "组织能力"], "careers": ["人力资源经理", "销售经理", "活动策划", "客户服务总监", "医疗卫生管理"], "cognitive_functions": "Fe-Si-Ne-Ti"},
    "ISTP": {"name": "鉴赏家", "desc": "大胆而实际的实验者，擅长使用各种工具，善于在实战中解决问题", "strengths": ["乐观", "精力充沛", "创造力", "务实", "动手能力强"], "careers": ["工程师", "飞行员", "消防员", "机械工程师", "技术运维"], "cognitive_functions": "Ti-Se-Ni-Fe"},
    "ISFP": {"name": "探险家", "desc": "灵活而有魅力的艺术家，随时准备探索和体验新事物，善于用感官体验世界", "strengths": ["迷人", "感知力强", "富有想象力", "好奇", "审美敏感"], "careers": ["设计师", "摄影师", "兽医", "时尚买手", "音乐制作人"], "cognitive_functions": "Fi-Se-Ni-Te"},
    "ESTP": {"name": "企业家", "desc": "聪明、精力充沛且非常善于感知的人，真正享受活在当下，善于解决即时问题", "strengths": ["大胆", "理性务实", "善于交际", "直接", "应变力"], "careers": ["销售精英", "企业家", "运动员/教练", "股票交易员", "危机管理顾问"], "cognitive_functions": "Se-Ti-Fe-Ni"},
    "ESFP": {"name": "表演者", "desc": "自发的、精力充沛的、热情的表演者，善于让周围人感到快乐和活力", "strengths": ["大胆", "独创性", "美学感", "善于交际", "感染力"], "careers": ["演员/主持人", "活动策划", "旅游顾问", "运动教练", "娱乐产业管理"], "cognitive_functions": "Se-Fi-Te-Ni"},
}

# ────────────────────────────────────────────────────────────
# 职业价值观维度描述
# ────────────────────────────────────────────────────────────

CV_DIMENSION_DESC = {
    "achievement": {
        "name": "成就感",
        "desc": "追求目标达成、获得认可与赞赏、不断超越自我，渴望在职业发展中看到明确的成果与进步",
        "career_suggestions": ["项目经理", "创业者", "销售精英", "咨询顾问", "研发工程师"],
    },
    "compensation": {
        "name": "经济报酬",
        "desc": "重视薪资福利和物质回报，希望获得与工作付出相匹配的经济补偿和长期财务保障",
        "career_suggestions": ["投资银行家", "基金经理", "管理咨询顾问", "企业高管", "技术销售"],
    },
    "independence": {
        "name": "自主性",
        "desc": "追求工作自由度和独立决策权，希望在工作中拥有更多的自主空间和自我掌控感",
        "career_suggestions": ["自由职业者", "研究人员", "软件开发者", "作家/艺术家", "咨询顾问"],
    },
    "altruism": {
        "name": "社会贡献",
        "desc": "希望通过工作为社会和他人带来价值，追求工作的意义感和社会影响力",
        "career_suggestions": ["公益组织管理", "教育工作者", "社会工作者", "医疗卫生专业", "环保工程师"],
    },
    "relationships": {
        "name": "人际关系",
        "desc": "重视团队氛围、上下级关系和职业社交网络，追求和谐互信的工作环境",
        "career_suggestions": ["人力资源经理", "团队建设专家", "培训师", "客户关系经理", "企业文化专员"],
    },
    "lifestyle": {
        "name": "工作环境",
        "desc": "关注工作场所舒适度、工作生活平衡和心理安全感，追求可持续的职业发展方式",
        "career_suggestions": ["远程工作者", "高校教师", "公共部门职员", "图书管理员", "健康管理师"],
    },
}


# ────────────────────────────────────────────────────────────
# 评分算法
# ────────────────────────────────────────────────────────────

def _answers_map(answers: list[AnswerItem]) -> dict[str, int]:
    return {a.question_id: a.score for a in answers}


def score_holland(answers: list[AnswerItem]) -> dict[str, Any]:
    am = _answers_map(answers)
    dims = {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}
    for q in HOLLAND_QUESTIONS:
        dims[q.dimension] += am.get(q.id, 3)
    sorted_dims = sorted(dims.items(), key=lambda x: -x[1])
    top3 = [d[0] for d in sorted_dims[:3]]
    holland_code = "".join(top3)
    top3_detail = []
    for code in top3:
        info = HOLLAND_TYPE_DESC[code]
        top3_detail.append({
            "code": code,
            "name": info["name"],
            "desc": info["desc"],
            "score": dims[code],
            "careers": info["careers"],
        })
    summary = f"你的 Holland 代码为 {holland_code}，属于{' / '.join(HOLLAND_TYPE_DESC[c]['name'] for c in top3)}类型"
    return {
        "scores": dims,
        "holland_code": holland_code,
        "top3": top3_detail,
        "summary": summary,
    }


def score_mbti(answers: list[AnswerItem]) -> dict[str, Any]:
    """
    EI: 1/2 -> E分，4/5 -> I分
    SN: 1/2 -> S分，4/5 -> N分
    TF: 1/2 -> T分，4/5 -> F分
    JP: 1/2 -> J分，4/5 -> P分
    """
    am = _answers_map(answers)
    dims: dict[str, dict[str, int]] = {
        "EI": {"E": 0, "I": 0},
        "SN": {"S": 0, "N": 0},
        "TF": {"T": 0, "F": 0},
        "JP": {"J": 0, "P": 0},
    }
    # 正向题（低分偏左字母，高分偏右字母）
    # EI题：1/2->E，4/5->I
    for q in MBTI_QUESTIONS:
        score = am.get(q.id, 3)
        d = q.dimension
        left_key, right_key = list(dims[d].keys())
        if score <= 2:
            dims[d][left_key] += (3 - score)
        elif score >= 4:
            dims[d][right_key] += (score - 3)
        # score == 3 不计分（中立）

    result_type = ""
    dim_results = {}
    for d, scores in dims.items():
        left_key, right_key = list(scores.keys())
        left_score = scores[left_key]
        right_score = scores[right_key]
        winner = left_key if left_score >= right_score else right_key
        result_type += winner
        dim_results[d] = {
            "left": {"letter": left_key, "score": left_score},
            "right": {"letter": right_key, "score": right_score},
            "winner": winner,
        }

    type_info = MBTI_TYPE_DESC.get(result_type, MBTI_TYPE_DESC["INTJ"])
    summary = f"你的 MBTI 类型为 {result_type}（{type_info['name']}）：{type_info['desc']}"
    return {
        "type": result_type,
        "dimensions": dim_results,
        "type_info": type_info,
        "summary": summary,
    }


def score_career_values(answers: list[AnswerItem]) -> dict[str, Any]:
    am = _answers_map(answers)
    dims: dict[str, list[int]] = defaultdict(list)
    for q in CAREER_VALUES_QUESTIONS:
        dims[q.dimension].append(am.get(q.id, 3))

    dim_scores = {k: round(sum(v) / len(v), 2) for k, v in dims.items()}
    sorted_dims = sorted(dim_scores.items(), key=lambda x: -x[1])
    top2 = [d[0] for d in sorted_dims[:2]]
    top_details = []
    for code in [d[0] for d in sorted_dims]:
        info = CV_DIMENSION_DESC[code]
        top_details.append({
            "code": code,
            "name": info["name"],
            "desc": info["desc"],
            "avg_score": dim_scores[code],
            "is_core": code in top2,
        })
    core_names = [CV_DIMENSION_DESC[c]["name"] for c in top2]
    summary = f"你的核心职业价值观为{' 与 '.join(core_names)}"
    return {
        "scores": dim_scores,
        "dimensions": top_details,
        "core_values": top2,
        "summary": summary,
    }


# ────────────────────────────────────────────────────────────
# 题库查询
# ────────────────────────────────────────────────────────────

def get_questions(assessment_type: str) -> AssessmentQuestionsResponse:
    meta = ASSESSMENT_META.get(assessment_type)
    if not meta:
        raise ValueError(f"不支持的测评类型: {assessment_type}")
    return AssessmentQuestionsResponse(
        type=assessment_type,
        title=meta["title"],
        description=meta["description"],
        questions=meta["questions"],
    )


def calculate_result(assessment_type: str, answers: list[AnswerItem]) -> dict[str, Any]:
    if assessment_type == "holland":
        result = score_holland(answers)
    elif assessment_type == "mbti":
        result = score_mbti(answers)
    elif assessment_type == "career_values":
        result = score_career_values(answers)
    else:
        raise ValueError(f"不支持的测评类型: {assessment_type}")
    return result


# ────────────────────────────────────────────────────────────
# 数据库 CRUD
# ────────────────────────────────────────────────────────────

async def save_assessment(
    db: AsyncSession,
    user_id: str,
    assessment_type: str,
    answers: list[AnswerItem],
) -> CareerAssessment:
    result = calculate_result(assessment_type, answers)
    summary = result.get("summary", "")
    record = CareerAssessment(
        user_id=user_id,
        type=assessment_type,
        answers=[a.model_dump() for a in answers],
        result=result,
        summary=summary,
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


async def get_user_assessments(
    db: AsyncSession,
    user_id: str,
) -> tuple[int, list[CareerAssessment]]:
    stmt = (
        select(CareerAssessment)
        .where(CareerAssessment.user_id == user_id)
        .order_by(desc(CareerAssessment.created_at))
    )
    rows = (await db.execute(stmt)).scalars().all()
    return len(rows), list(rows)


async def get_assessment_by_id(
    db: AsyncSession,
    user_id: str,
    assessment_id: str,
) -> CareerAssessment | None:
    stmt = select(CareerAssessment).where(
        CareerAssessment.id == assessment_id,
        CareerAssessment.user_id == user_id,
    )
    return (await db.execute(stmt)).scalar_one_or_none()


# ────────────────────────────────────────────────────────────
# AI 岗位匹配推荐（Deepseek 流式）
# ────────────────────────────────────────────────────────────

RECOMMEND_PROMPT = """你是一位资深职业规划师。请根据以下测评结果{resume_hint}，为用户推荐最匹配的岗位方向并提供面试准备建议。

测评类型：{test_type}
测评结果摘要：{summary}
测评详细数据：
{result_detail}

{resume_section}

请严格按以下 JSON 格式返回，不要其他内容：
{{
  "jobs": [
    {{
      "title": "岗位名称",
      "match": 92,
      "reason": "结合测评结果说明为何匹配（不超过40字）",
      "salary_range": "15K-25K"
    }}
  ],
  "prep_tips": [
    {{
      "category": "分类名称（如：技术能力、行为面试、行业知识）",
      "tips": ["具体建议1", "具体建议2", "具体建议3"]
    }}
  ]
}}

要求：
1. jobs 数组推荐 5 个岗位，按匹配度从高到低排列，match 为 0-100 的整数
2. salary_range 为国内一线城市大致月薪范围（如 10K-20K）
3. prep_tips 包含 3-4 个分类，每个分类 3-4 条具体可执行的建议
4. 只返回 JSON，不要其他内容"""


def _build_result_detail(test_type: str, result: dict[str, Any]) -> str:
    """将测评结果格式化为可读文本"""
    if test_type == "holland":
        code = result.get("holland_code", "")
        scores = result.get("scores", {})
        top3 = result.get("top3", [])
        lines = [f"霍兰德代码：{code}"]
        lines += [f"六维度得分：{', '.join(f'{k}={v}' for k, v in scores.items())}"]
        for t in top3:
            lines.append(f"  Top {t['code']}({t['name']}): {t['score']}分 - {t['desc'][:50]}")
        return "\n".join(lines)
    elif test_type == "mbti":
        mbti_type = result.get("type", "")
        dims = result.get("dimensions", {})
        lines = [f"MBTI 类型：{mbti_type}"]
        for k, v in dims.items():
            lines.append(f"  {k} 维度：{v['left']['letter']}={v['left']['score']} vs {v['right']['letter']}={v['right']['score']}，倾向：{v['winner']}")
        return "\n".join(lines)
    elif test_type == "career_values":
        core = result.get("core_values", [])
        scores = result.get("scores", {})
        lines = [f"核心价值观：{', '.join(core)}"]
        lines += [f"各维度均分：{', '.join(f'{k}={v}' for k, v in scores.items())}"]
        return "\n".join(lines)
    return str(result)


async def generate_career_recommendation_stream(
    test_type: str,
    result: dict[str, Any],
    summary: str,
    skill_keywords: list[str] | None = None,
):
    """流式调用 Deepseek，逐条 yield NDJSON 行"""
    result_detail = _build_result_detail(test_type, result)

    resume_section = ""
    resume_hint = ""
    if skill_keywords:
        resume_hint = "和简历技能栈"
        resume_section = f"用户简历技能关键词：{', '.join(skill_keywords[:15])}"

    prompt = RECOMMEND_PROMPT.format(
        test_type=test_type,
        summary=summary,
        result_detail=result_detail,
        resume_section=resume_section,
        resume_hint=resume_hint,
    )

    url = f"{_settings.deepseek_api_url.rstrip('/')}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {_settings.deepseek_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": _settings.deepseek_model,
        "messages": [
            {"role": "system", "content": "你是一位专业的职业规划师，擅长根据心理测评结果和技能背景为用户提供精准的职业方向建议和面试准备指导。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.4,
        "max_tokens": 3000,
        "stream": True,
    }

    buffer = ""
    full_buffer = ""  # 完整累积，用于流结束后提取 prep_tips
    jobs_sent = 0
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
                full_buffer += content

                # 尝试从 buffer 中提取完整的 job 对象
                while True:
                    m = re.search(r'\{[^{}]*"title"[^{}]*"match"[^{}]*"salary_range"[^{}]*\}', buffer)
                    if not m:
                        break
                    try:
                        job = json.loads(m.group())
                        buffer = buffer[m.end():]
                        jobs_sent += 1
                        yield json.dumps(
                            {"type": "job", "index": jobs_sent - 1, "data": job},
                            ensure_ascii=False,
                        )
                    except json.JSONDecodeError:
                        break

    # 流结束后，从 full_buffer（完整响应）提取 prep_tips
    tips_match = re.search(r'"prep_tips"\s*:\s*(\[[\s\S]*?\])\s*\}', full_buffer)
    prep_tips = []
    if tips_match:
        try:
            prep_tips = json.loads(tips_match.group(1))
        except json.JSONDecodeError:
            pass

    # 如果无法从流式 full_buffer 提取，做整体兜底解析
    if not prep_tips:
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', full_buffer)
        full_text = json_match.group(1).strip() if json_match else full_buffer
        try:
            full_data = json.loads(full_text)
            prep_tips = full_data.get("prep_tips", [])
        except json.JSONDecodeError:
            pass

    yield json.dumps(
        {"type": "done", "prep_tips": prep_tips, "total_jobs": jobs_sent},
        ensure_ascii=False,
    )
