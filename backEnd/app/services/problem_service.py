import json
from datetime import datetime

from sqlalchemy import func, select, and_, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.problem import Problem, Submission
from app.models.user import User
from app.schemas.problem import (
    ProblemDetail,
    ProblemListItem,
    SubmissionResponse,
    UserProgressResponse,
    DifficultyProgress,
    TagProgress,
    DebugResponse,
)
from app.services.code_executor import execute_code, ExecuteResult


# ---------- Problem Queries ----------


async def get_problems(
    db: AsyncSession,
    *,
    difficulty: str | None = None,
    tag: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    size: int = 20,
    user_id: str | None = None,
) -> tuple[list[Problem], int]:
    """获取题目列表（支持筛选）"""
    conditions = []

    if difficulty:
        conditions.append(Problem.difficulty == difficulty)
    if tag:
        conditions.append(Problem.tags.ilike(f"%{tag}%"))
    if keyword:
        conditions.append(
            Problem.title.ilike(f"%{keyword}%")
            | Problem.description.ilike(f"%{keyword}%")
        )

    where_clause = and_(*conditions) if conditions else True

    # 总数
    count_stmt = select(func.count()).select_from(Problem).where(where_clause)
    total = (await db.execute(count_stmt)).scalar_one()

    # 分页查询
    stmt = (
        select(Problem)
        .where(where_clause)
        .order_by(Problem.display_id.asc())
        .offset((page - 1) * size)
        .limit(size)
    )
    result = await db.execute(stmt)
    problems = list(result.scalars().all())

    return problems, total


async def get_problem(db: AsyncSession, problem_id: str) -> Problem | None:
    """获取单个题目详情"""
    stmt = select(Problem).where(Problem.id == problem_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_problem_by_display_id(
    db: AsyncSession, display_id: str
) -> Problem | None:
    """通过显示ID获取题目"""
    stmt = select(Problem).where(Problem.display_id == display_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# ---------- Submission Queries ----------


from dataclasses import dataclass


@dataclass
class SubmissionResult:
    submission: Submission
    error_detail: str = ""


async def create_submission(
    db: AsyncSession,
    user: User,
    problem: Problem,
    code: str,
    language: str,
) -> SubmissionResult:
    """提交代码 - 实际执行判题"""
    # 解析样例输入输出
    try:
        sample_inputs = json.loads(problem.sample_input) if problem.sample_input else []
        sample_outputs = json.loads(problem.sample_output) if problem.sample_output else []
    except json.JSONDecodeError:
        sample_inputs = []
        sample_outputs = []

    # 对每组样例执行判题
    all_accepted = True
    total_time = 0
    max_memory = 0
    error_detail = ""

    if not sample_inputs:
        # 无样例数据，直接 accepted
        status = "accepted"
    else:
        for idx, sample_in in enumerate(sample_inputs):
            result = await execute_code(
                code=code,
                language=language,
                input_data=sample_in,
                time_limit_ms=problem.time_limit,
            )
            total_time = max(total_time, result.execution_time)

            if result.status == "compilation_error":
                all_accepted = False
                status = "compilation_error"
                error_detail = result.stderr if result.stderr.strip() else "编译失败，请检查代码语法"
                break
            elif result.status == "time_limit_exceeded":
                all_accepted = False
                status = "time_limit_exceeded"
                error_detail = "程序运行超时，请优化算法时间复杂度"
                break
            elif result.status == "runtime_error":
                all_accepted = False
                status = "runtime_error"
                error_detail = result.stderr if result.stderr.strip() else "程序运行时出错，请检查数组越界、空指针等问题"
                break
            else:
                # 比较输出（统一换行符 + 忽略首尾空白 + 逐行对比）
                expected_raw = sample_outputs[idx] if idx < len(sample_outputs) else ""
                actual_raw = result.stdout
                # 统一 \r\n -> \n，去除首尾空白，按行比较
                expected_lines = [l.strip() for l in expected_raw.replace('\r\n', '\n').replace('\r', '\n').strip().split('\n') if l.strip() != '']
                actual_lines = [l.strip() for l in actual_raw.replace('\r\n', '\n').replace('\r', '\n').strip().split('\n') if l.strip() != '']
                if actual_lines != expected_lines:
                    all_accepted = False
                    status = "wrong_answer"
                    error_detail = f"样例 {idx + 1} 输出不匹配，请检查逻辑"
                    break

        if all_accepted and sample_inputs:
            status = "accepted"

    submission = Submission(
        user_id=user.id,
        problem_id=problem.id,
        code=code,
        language=language,
        status=status,
        execution_time=total_time,
        execution_memory=max_memory,
    )
    db.add(submission)

    # 更新题目统计
    problem.total_submissions += 1
    if status == "accepted":
        problem.accepted_submissions += 1

    await db.flush()
    await db.refresh(submission)
    return SubmissionResult(submission=submission, error_detail=error_detail)


async def debug_code(
    code: str,
    language: str,
    input_data: str,
    time_limit_ms: int = 5000,
) -> DebugResponse:
    """调试代码 - 执行并返回输出"""
    result = await execute_code(
        code=code,
        language=language,
        input_data=input_data,
        time_limit_ms=time_limit_ms,
    )
    return DebugResponse(
        stdout=result.stdout,
        stderr=result.stderr,
        exit_code=result.exit_code,
        execution_time=result.execution_time,
        status=result.status,
    )


async def get_user_submissions(
    db: AsyncSession,
    user_id: str,
    problem_id: str | None = None,
    limit: int = 20,
) -> list[Submission]:
    """获取用户提交记录"""
    conditions = [Submission.user_id == user_id]
    if problem_id:
        conditions.append(Submission.problem_id == problem_id)

    stmt = (
        select(Submission)
        .where(and_(*conditions))
        .order_by(Submission.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def check_user_solved(
    db: AsyncSession, user_id: str, problem_ids: list[str]
) -> set[str]:
    """检查用户已通过的题目"""
    if not problem_ids or not user_id:
        return set()

    stmt = (
        select(distinct(Submission.problem_id))
        .where(
            and_(
                Submission.user_id == user_id,
                Submission.status == "accepted",
                Submission.problem_id.in_(problem_ids),
            )
        )
    )
    result = await db.execute(stmt)
    return set(result.scalars().all())


# ---------- Progress Queries ----------


async def get_user_progress(
    db: AsyncSession,
    user_id: str,
) -> UserProgressResponse:
    """获取用户进度统计"""
    # 总提交数和通过数
    stmt = select(
        func.count().label("total"),
        func.sum(
            func.if_(Submission.status == "accepted", 1, 0)
        ).label("accepted"),
    ).where(Submission.user_id == user_id)
    result = await db.execute(stmt)
    row = result.one()
    total_submissions = row.total or 0
    total_accepted = row.accepted or 0

    # 尝试的题目数
    stmt = select(func.count(distinct(Submission.problem_id))).where(
        Submission.user_id == user_id
    )
    attempted = (await db.execute(stmt)).scalar_one()

    # 通过的题目数
    stmt = select(func.count(distinct(Submission.problem_id))).where(
        and_(Submission.user_id == user_id, Submission.status == "accepted")
    )
    solved = (await db.execute(stmt)).scalar_one()

    # 按难度统计
    difficulties = ["easy", "medium", "hard"]
    by_difficulty = []
    for diff in difficulties:
        # 该难度的总题目数
        stmt = select(func.count()).select_from(Problem).where(
            Problem.difficulty == diff
        )
        total_problems = (await db.execute(stmt)).scalar_one()

        # 用户已通过的该难度题目数
        stmt = select(func.count(distinct(Submission.problem_id))).where(
            and_(
                Submission.user_id == user_id,
                Submission.status == "accepted",
                Submission.problem_id.in_(
                    select(Problem.id).where(Problem.difficulty == diff)
                ),
            )
        )
        diff_solved = (await db.execute(stmt)).scalar_one()

        # 用户已尝试的该难度题目数
        stmt = select(func.count(distinct(Submission.problem_id))).where(
            and_(
                Submission.user_id == user_id,
                Submission.problem_id.in_(
                    select(Problem.id).where(Problem.difficulty == diff)
                ),
            )
        )
        diff_attempted = (await db.execute(stmt)).scalar_one()

        by_difficulty.append(
            DifficultyProgress(
                difficulty=diff,
                total_problems=total_problems,
                solved=diff_solved,
                attempted=diff_attempted,
            )
        )

    # 按标签统计
    all_tags = await get_all_tags(db)
    by_tag = []
    for tag_name in all_tags[:15]:  # 限制最多15个标签
        # 该标签的总题目数
        stmt = select(func.count()).select_from(Problem).where(
            Problem.tags.ilike(f"%{tag_name}%")
        )
        tag_total = (await db.execute(stmt)).scalar_one()

        # 用户已通过的该标签题目数
        stmt = select(func.count(distinct(Submission.problem_id))).where(
            and_(
                Submission.user_id == user_id,
                Submission.status == "accepted",
                Submission.problem_id.in_(
                    select(Problem.id).where(Problem.tags.ilike(f"%{tag_name}%"))
                ),
            )
        )
        tag_solved = (await db.execute(stmt)).scalar_one()

        by_tag.append(TagProgress(tag=tag_name, total=tag_total, solved=tag_solved))

    # 最近提交记录
    recent = await get_user_submissions(db, user_id, limit=10)

    return UserProgressResponse(
        total_submissions=total_submissions,
        total_accepted=total_accepted,
        total_problems_attempted=attempted,
        total_problems_solved=solved,
        by_difficulty=by_difficulty,
        by_tag=by_tag,
        recent_submissions=[
            SubmissionResponse(
                id=s.id,
                problem_id=s.problem_id,
                code=s.code[:100] + "..." if len(s.code) > 100 else s.code,
                language=s.language,
                status=s.status,
                execution_time=s.execution_time,
                execution_memory=s.execution_memory,
                created_at=s.created_at,
            )
            for s in recent
        ],
    )


async def get_all_tags(db: AsyncSession) -> list[str]:
    """获取所有标签"""
    stmt = select(Problem.tags)
    result = await db.execute(stmt)
    tag_set = set()
    for row in result.scalars().all():
        if row:
            for tag in row.split(","):
                tag = tag.strip()
                if tag:
                    tag_set.add(tag)
    return sorted(tag_set)


# ---------- Helper ----------


def build_problem_list_item(
    problem: Problem, user_solved_ids: set[str] | None = None
) -> ProblemListItem:
    """构建题目列表项"""
    rate = 0.0
    if problem.total_submissions > 0:
        rate = round(
            problem.accepted_submissions / problem.total_submissions * 100, 1
        )

    return ProblemListItem(
        id=problem.id,
        display_id=problem.display_id,
        title=problem.title,
        difficulty=problem.difficulty,
        tags=problem.tags,
        total_submissions=problem.total_submissions,
        accepted_submissions=problem.accepted_submissions,
        acceptance_rate=rate,
        user_solved=problem.id in user_solved_ids if user_solved_ids else False,
    )


def build_problem_detail(
    problem: Problem, user_solved: bool = False
) -> ProblemDetail:
    """构建题目详情"""
    rate = 0.0
    if problem.total_submissions > 0:
        rate = round(
            problem.accepted_submissions / problem.total_submissions * 100, 1
        )

    return ProblemDetail(
        id=problem.id,
        display_id=problem.display_id,
        title=problem.title,
        description=problem.description,
        input_format=problem.input_format,
        output_format=problem.output_format,
        constraints=problem.constraints,
        sample_input=problem.sample_input,
        sample_output=problem.sample_output,
        hint=problem.hint,
        time_limit=problem.time_limit,
        memory_limit=problem.memory_limit,
        difficulty=problem.difficulty,
        tags=problem.tags,
        total_submissions=problem.total_submissions,
        accepted_submissions=problem.accepted_submissions,
        acceptance_rate=rate,
        user_solved=user_solved,
        created_at=problem.created_at,
        updated_at=problem.updated_at,
    )


# ---------- Seed Data ----------


SEED_PROBLEMS = [
    {
        "display_id": "1001",
        "title": "两数之和",
        "description": "给定一个整数数组 nums 和一个整数目标值 target，请你在该数组中找出和为目标值 target 的那两个整数，并返回它们的数组下标。\n\n你可以假设每种输入只会对应一个答案，并且你不能使用两次相同的元素。\n\n你可以按任意顺序返回答案。",
        "input_format": "第一行包含一个整数 n，表示数组长度。\n第二行包含 n 个整数，表示数组元素。\n第三行包含一个整数 target。",
        "output_format": "输出两个整数，表示满足条件的两个元素的下标（空格分隔）。",
        "constraints": "2 <= n <= 10^4\n-10^9 <= nums[i] <= 10^9\n-10^9 <= target <= 10^9\n只会存在一个有效答案",
        "sample_input": json.dumps(["4\n2 7 11 15\n9", "3\n3 2 4\n6"]),
        "sample_output": json.dumps(["0 1", "1 2"]),
        "hint": "第一组样例：nums[0] + nums[1] = 2 + 7 = 9，所以返回 [0, 1]。\n第二组样例：nums[1] + nums[2] = 2 + 4 = 6，所以返回 [1, 2]。",
        "time_limit": 1000,
        "memory_limit": 256,
        "difficulty": "easy",
        "tags": "数组,哈希表",
    },
    {
        "display_id": "1002",
        "title": "反转链表",
        "description": "给你单链表的头节点 head，请你反转链表，并返回反转后的链表。\n\n链表节点定义：\nVal  int\nNext *ListNode",
        "input_format": "第一行包含一个整数 n，表示链表节点数。\n第二行包含 n 个整数，表示链表各节点的值。",
        "output_format": "输出 n 个整数，表示反转后链表各节点的值（空格分隔）。",
        "constraints": "链表中节点的数目范围是 [0, 5000]\n-5000 <= Node.val <= 5000",
        "sample_input": json.dumps(["5\n1 2 3 4 5", "3\n1 2"]),
        "sample_output": json.dumps(["5 4 3 2 1", "2 1"]),
        "hint": "使用三个指针 prev、curr、next 依次反转链表指针方向。",
        "time_limit": 1000,
        "memory_limit": 256,
        "difficulty": "easy",
        "tags": "链表,双指针",
    },
    {
        "display_id": "1003",
        "title": "最长回文子串",
        "description": "给你一个字符串 s，找到 s 中最长的回文子串。\n\n如果字符串的反序与原始字符串相同，则该字符串称为回文字符串。",
        "input_format": "一行一个字符串 s。",
        "output_format": "输出最长回文子串。",
        "constraints": "1 <= s.length <= 1000\ns 仅由数字和英文字母组成",
        "sample_input": json.dumps(["babad", "cbba"]),
        "sample_output": json.dumps(["bab", "bb"]),
        "hint": "可以使用中心扩展法或 Manacher 算法。对于每个字符，向两边扩展检查是否为回文。",
        "time_limit": 2000,
        "memory_limit": 256,
        "difficulty": "medium",
        "tags": "字符串,动态规划",
    },
    {
        "display_id": "1004",
        "title": "合并区间",
        "description": "以数组 intervals 表示若干个区间的集合，其中单个区间为 intervals[i] = [start_i, end_i]。请你合并所有重叠的区间，并返回一个不重叠的区间数组，该数组需恰好覆盖输入中的所有区间。",
        "input_format": "第一行包含一个整数 n，表示区间数量。\n接下来 n 行，每行两个整数 start 和 end。",
        "output_format": "输出合并后的区间，每行两个整数表示一个区间。",
        "constraints": "1 <= intervals.length <= 10^4\nintervals[i].length == 2\n0 <= start_i <= end_i <= 10^4",
        "sample_input": json.dumps(["4\n1 3\n2 6\n8 10\n15 18"]),
        "sample_output": json.dumps(["1 6\n8 10\n15 18"]),
        "hint": "先按区间起始位置排序，然后依次判断当前区间是否与上一个合并后的区间重叠。",
        "time_limit": 1000,
        "memory_limit": 256,
        "difficulty": "medium",
        "tags": "数组,排序",
    },
    {
        "display_id": "1005",
        "title": "二叉树的层序遍历",
        "description": "给你二叉树的根节点 root，返回其节点值的层序遍历（即逐层地，从左到右访问所有节点）。\n\n每一层的节点值放在一个单独的列表中。",
        "input_format": "第一行包含一个整数 n，表示节点数。\n第二行包含 n 个整数（-1 表示空节点），按层序给出二叉树。",
        "output_format": "每行输出一个层的节点值，空格分隔。",
        "constraints": "树中节点数目在范围 [0, 2000] 内\n-1000 <= Node.val <= 1000",
        "sample_input": json.dumps(["7\n3 9 20 -1 -1 15 7"]),
        "sample_output": json.dumps(["3\n9 20\n15 7"]),
        "hint": "使用 BFS（广度优先搜索），借助队列实现层序遍历。",
        "time_limit": 1000,
        "memory_limit": 256,
        "difficulty": "medium",
        "tags": "树,广度优先搜索",
    },
    {
        "display_id": "1006",
        "title": "最长递增子序列",
        "description": "给你一个整数数组 nums，找到其中最长严格递增子序列的长度。\n\n子序列不要求连续，但需要保持相对顺序。",
        "input_format": "第一行包含一个整数 n。\n第二行包含 n 个整数。",
        "output_format": "输出一个整数，表示最长递增子序列的长度。",
        "constraints": "1 <= nums.length <= 2500\n-10^4 <= nums[i] <= 10^4",
        "sample_input": json.dumps(["6\n10 9 2 5 3 7"]),
        "sample_output": json.dumps(["3"]),
        "hint": "定义 dp[i] 为以 nums[i] 结尾的最长递增子序列长度。对于每个 j < i，如果 nums[j] < nums[i]，则 dp[i] = max(dp[i], dp[j] + 1)。",
        "time_limit": 1000,
        "memory_limit": 256,
        "difficulty": "medium",
        "tags": "动态规划,数组",
    },
    {
        "display_id": "1007",
        "title": "接雨水",
        "description": "给定 n 个非负整数表示每个宽度为 1 的柱子的高度图，计算按此排列的柱子，下雨之后能接多少雨水。",
        "input_format": "第一行包含一个整数 n。\n第二行包含 n 个非负整数，表示每个柱子的高度。",
        "output_format": "输出一个整数，表示能接住的雨水总量。",
        "constraints": "n == height.length\n1 <= n <= 2 * 10^4\n0 <= height[i] <= 10^5",
        "sample_input": json.dumps(["12\n0 1 0 2 1 0 1 3 2 1 2 1"]),
        "sample_output": json.dumps(["6"]),
        "hint": "对于每个位置，能接的水 = min(左边最高, 右边最高) - 当前高度。可以使用双指针或预处理左右最大值。",
        "time_limit": 1000,
        "memory_limit": 256,
        "difficulty": "hard",
        "tags": "数组,双指针,动态规划",
    },
    {
        "display_id": "1008",
        "title": "合并K个升序链表",
        "description": "给你一个链表数组，每个链表都已经按升序排列。\n\n请你将所有链表合并到一个升序链表中，返回合并后的链表。",
        "input_format": "第一行包含一个整数 k，表示链表数量。\n接下来 k 组数据，每组第一行为链表长度 n，第二行为 n 个整数。",
        "output_format": "输出合并后的升序链表，空格分隔。",
        "constraints": "k == lists.length\n0 <= k <= 10^4\n0 <= lists[i].length <= 500\n-10^4 <= lists[i][j] <= 10^4",
        "sample_input": json.dumps(["3\n3\n1 4 5\n3\n1 3 4\n2\n2 6"]),
        "sample_output": json.dumps(["1 1 2 3 4 4 5 6"]),
        "hint": "使用最小堆（优先队列）维护每个链表的当前最小节点，每次取出最小节点并推进该链表。",
        "time_limit": 2000,
        "memory_limit": 256,
        "difficulty": "hard",
        "tags": "链表,分治,堆",
    },
    {
        "display_id": "1009",
        "title": "有效的括号",
        "description": "给定一个只包括 '('，')'，'{'，'}'，'['，']' 的字符串 s，判断字符串是否有效。\n\n有效字符串需满足：\n1. 左括号必须用相同类型的右括号闭合。\n2. 左括号必须以正确的顺序闭合。",
        "input_format": "一行一个字符串 s。",
        "output_format": "输出 true 或 false。",
        "constraints": "1 <= s.length <= 10^4\ns 仅由括号 '()[]{}' 组成",
        "sample_input": json.dumps(["()", "()[]{}", "(]"]),
        "sample_output": json.dumps(["true", "true", "false"]),
        "hint": "使用栈，遇到左括号入栈，遇到右括号检查栈顶是否匹配。",
        "time_limit": 1000,
        "memory_limit": 128,
        "difficulty": "easy",
        "tags": "栈,字符串",
    },
    {
        "display_id": "1010",
        "title": "全排列",
        "description": "给定一个不含重复数字的数组 nums，返回其所有可能的全排列。\n\n你可以按任意顺序返回答案。",
        "input_format": "第一行包含一个整数 n。\n第二行包含 n 个互不相同的整数。",
        "output_format": "每行输出一个排列，数字空格分隔。按字典序输出。",
        "constraints": "1 <= nums.length <= 6\n-10 <= nums[i] <= 10\nnums 中的所有整数互不相同",
        "sample_input": json.dumps(["3\n1 2 3"]),
        "sample_output": json.dumps(["1 2 3\n1 3 2\n2 1 3\n2 3 1\n3 1 2\n3 2 1"]),
        "hint": "使用回溯算法，通过交换元素位置生成所有排列。",
        "time_limit": 1000,
        "memory_limit": 256,
        "difficulty": "medium",
        "tags": "回溯,递归",
    },
    {
        "display_id": "1011",
        "title": "二分查找",
        "description": "给定一个 n 个元素有序的（升序）整型数组 nums 和一个目标值 target，写一个函数搜索 nums 中的 target，如果目标值存在返回下标，否则返回 -1。",
        "input_format": "第一行包含一个整数 n，表示数组长度。\n第二行包含 n 个升序整数。\n第三行包含一个整数 target。",
        "output_format": "输出目标值的下标，若不存在则输出 -1。",
        "constraints": "1 <= n <= 10^4\n-10^4 <= nums[i] <= 10^4\nnums 中的所有整数是不重复的",
        "sample_input": json.dumps(["6\n-1 0 3 5 9 12\n9", "6\n-1 0 3 5 9 12\n2"]),
        "sample_output": json.dumps(["4", "-1"]),
        "hint": "使用二分查找算法，设置左右指针，每次取中间值与目标比较。",
        "time_limit": 1000,
        "memory_limit": 256,
        "difficulty": "easy",
        "tags": "数组,二分查找",
    },
    {
        "display_id": "1012",
        "title": "爬楼梯",
        "description": "假设你正在爬楼梯。需要 n 阶你才能到达楼顶。\n\n每次你可以爬 1 或 2 个台阶。你有多少种不同的方法可以爬到楼顶？",
        "input_format": "一行一个整数 n。",
        "output_format": "输出一个整数，表示爬楼梯的方法数。",
        "constraints": "1 <= n <= 45",
        "sample_input": json.dumps(["3", "5"]),
        "sample_output": json.dumps(["3", "8"]),
        "hint": "这是一个经典的斐波那契数列问题。dp[i] = dp[i-1] + dp[i-2]。",
        "time_limit": 1000,
        "memory_limit": 256,
        "difficulty": "easy",
        "tags": "动态规划,数学",
    },
    {
        "display_id": "1013",
        "title": "最大子数组和",
        "description": "给你一个整数数组 nums，请你找出一个具有最大和的连续子数组（子数组最少包含一个元素），返回其最大和。\n\n子数组是数组中的一个连续部分。",
        "input_format": "第一行包含一个整数 n。\n第二行包含 n 个整数。",
        "output_format": "输出最大子数组和。",
        "constraints": "1 <= nums.length <= 10^5\n-10^4 <= nums[i] <= 10^4",
        "sample_input": json.dumps(["9\n-2 1 -3 4 -1 2 1 -5 4", "1\n-1"]),
        "sample_output": json.dumps(["6", "-1"]),
        "hint": "使用 Kadane 算法：遍历数组，维护当前子数组和 cur，若 cur < 0 则重新开始。",
        "time_limit": 1000,
        "memory_limit": 256,
        "difficulty": "medium",
        "tags": "动态规划,数组",
    },
    {
        "display_id": "1014",
        "title": "三数之和",
        "description": "给你一个整数数组 nums，判断是否存在三元组 [nums[i], nums[j], nums[k]] 满足 i != j != k，且 nums[i] + nums[j] + nums[k] == 0。\n\n请你返回所有和为 0 且不重复的三元组。",
        "input_format": "第一行包含一个整数 n。\n第二行包含 n 个整数。",
        "output_format": "每行输出一个三元组，数字空格分隔。按字典序输出。",
        "constraints": "3 <= nums.length <= 3000\n-10^5 <= nums[i] <= 10^5",
        "sample_input": json.dumps(["6\n-1 0 1 2 -1 -4"]),
        "sample_output": json.dumps(["-1 -1 2\n-1 0 1"]),
        "hint": "先排序，然后固定一个数，用双指针在剩余部分寻找两数之和。注意去重。",
        "time_limit": 2000,
        "memory_limit": 256,
        "difficulty": "medium",
        "tags": "数组,双指针,排序",
    },
    {
        "display_id": "1015",
        "title": "岛屿数量",
        "description": "给你一个由 '1'（陆地）和 '0'（水）组成的的二维网格，请你计算网格中岛屿的数量。\n\n岛屿总是被水包围，并且每座岛屿只能由水平方向和/或竖直方向上相邻的陆地连接形成。",
        "input_format": "第一行两个整数 m 和 n，表示网格的行数和列数。\n接下来 m 行，每行 n 个字符（'0' 或 '1'）。",
        "output_format": "输出一个整数，表示岛屿数量。",
        "constraints": "1 <= m, n <= 300\ngrid[i][j] 的值为 '0' 或 '1'",
        "sample_input": json.dumps(["4 5\n1 1 0 0 0\n1 1 0 0 0\n0 0 1 0 0\n0 0 0 1 1"]),
        "sample_output": json.dumps(["3"]),
        "hint": "遍历网格，遇到 '1' 时进行 DFS/BFS 将整座岛标记为已访问，计数加一。",
        "time_limit": 2000,
        "memory_limit": 256,
        "difficulty": "medium",
        "tags": "深度优先搜索,广度优先搜索,矩阵",
    },
    {
        "display_id": "1016",
        "title": "从前序与中序遍历序列构造二叉树",
        "description": "给定两个整数数组 preorder 和 inorder，其中 preorder 是二叉树的先序遍历，inorder 是同一棵树的中序遍历，请你构造二叉树并返回其根节点。\n\n输出该二叉树的后序遍历结果。",
        "input_format": "第一行包含一个整数 n。\n第二行包含 n 个整数，表示先序遍历。\n第三行包含 n 个整数，表示中序遍历。",
        "output_format": "输出后序遍历结果，空格分隔。",
        "constraints": "1 <= n <= 3000\n-3000 <= preorder[i], inorder[i] <= 3000\npreorder 和 inorder 均无重复元素",
        "sample_input": json.dumps(["7\n3 9 20 15 7\n9 3 15 20 7"]),
        "sample_output": json.dumps(["9 15 7 20 3"]),
        "hint": "先序遍历的第一个元素是根节点，在中序遍历中找到根节点位置，递归构建左右子树。",
        "time_limit": 1000,
        "memory_limit": 256,
        "difficulty": "medium",
        "tags": "树,递归,二叉树",
    },
    {
        "display_id": "1017",
        "title": "零钱兑换",
        "description": "给你一个整数数组 coins，表示不同面额的硬币；以及一个整数 amount，表示总金额。\n\n计算并返回可以凑成总金额所需的最少的硬币个数。如果没有任何一种硬币组合能组成总金额，返回 -1。\n\n你可以认为每种硬币的数量是无限的。",
        "input_format": "第一行包含一个整数 n，表示硬币种类数。\n第二行包含 n 个整数，表示各硬币面额。\n第三行包含一个整数 amount。",
        "output_format": "输出最少硬币数，若无法凑出则输出 -1。",
        "constraints": "1 <= coins.length <= 12\n1 <= coins[i] <= 2^31 - 1\n0 <= amount <= 10^4",
        "sample_input": json.dumps(["3\n1 2 5\n11", "1\n2\n3"]),
        "sample_output": json.dumps(["3", "-1"]),
        "hint": "完全背包问题。dp[j] 表示凑成金额 j 所需的最少硬币数，dp[j] = min(dp[j], dp[j - coins[i]] + 1)。",
        "time_limit": 1000,
        "memory_limit": 256,
        "difficulty": "medium",
        "tags": "动态规划,背包",
    },
    {
        "display_id": "1018",
        "title": "最长公共子序列",
        "description": "给定两个字符串 text1 和 text2，返回这两个字符串的最长公共子序列的长度。\n\n一个字符串的子序列是指这样一个新的字符串：它是由原字符串在不改变字符的相对顺序的情况下删除某些字符后组成的新字符串。",
        "input_format": "第一行一个字符串 text1。\n第二行一个字符串 text2。",
        "output_format": "输出最长公共子序列的长度。",
        "constraints": "1 <= text1.length, text2.length <= 1000\ntext1 和 text2 仅由小写英文字符组成",
        "sample_input": json.dumps(["abcde", "ace"]),
        "sample_output": json.dumps(["3"]),
        "hint": "经典二维 DP。dp[i][j] 表示 text1 前 i 个字符和 text2 前 j 个字符的 LCS 长度。",
        "time_limit": 1000,
        "memory_limit": 256,
        "difficulty": "medium",
        "tags": "动态规划,字符串",
    },
    {
        "display_id": "1019",
        "title": "滑动窗口最大值",
        "description": "给你一个整数数组 nums，有一个大小为 k 的滑动窗口从数组的最左侧移动到数组的最右侧。你只可以看到在滑动窗口内的 k 个数字。滑动窗口每次只向右移动一位。\n\n返回滑动窗口中的最大值。",
        "input_format": "第一行包含一个整数 n。\n第二行包含 n 个整数。\n第三行包含一个整数 k。",
        "output_format": "输出每个窗口的最大值，空格分隔。",
        "constraints": "1 <= nums.length <= 10^5\n-10^4 <= nums[i] <= 10^4\n1 <= k <= nums.length",
        "sample_input": json.dumps(["8\n1 3 -1 -3 5 3 6 7\n3"]),
        "sample_output": json.dumps(["3 3 5 5 6 7"]),
        "hint": "使用单调递减双端队列，队列中存储下标。窗口右移时，移除超出窗口范围的元素，加入新元素并维护单调性。",
        "time_limit": 2000,
        "memory_limit": 256,
        "difficulty": "hard",
        "tags": "单调队列,滑动窗口,数组",
    },
    {
        "display_id": "1020",
        "title": "编辑距离",
        "description": "给你两个单词 word1 和 word2，请返回将 word1 转换成 word2 所使用的最少操作数。\n\n你可以对一个单词进行如下三种操作：\n1. 插入一个字符\n2. 删除一个字符\n3. 替换一个字符",
        "input_format": "第一行一个字符串 word1。\n第二行一个字符串 word2。",
        "output_format": "输出最少操作数。",
        "constraints": "1 <= word1.length, word2.length <= 500\nword1 和 word2 仅由小写英文字母组成",
        "sample_input": json.dumps(["horse", "ros"]),
        "sample_output": json.dumps(["3"]),
        "hint": "dp[i][j] 表示 word1 前 i 个字符转换成 word2 前 j 个字符的最少操作数。若 word1[i-1] == word2[j-1]，dp[i][j] = dp[i-1][j-1]；否则取三种操作的最小值加 1。",
        "time_limit": 1000,
        "memory_limit": 256,
        "difficulty": "medium",
        "tags": "动态规划,字符串",
    },
    {
        "display_id": "1021",
        "title": "环形链表",
        "description": "给你一个链表的头节点 head，判断链表中是否有环。\n\n如果链表中有某个节点，可以通过连续跟踪 next 指针再次到达，则链表中存在环。",
        "input_format": "第一行包含一个整数 n，表示链表节点数。\n第二行包含 n 个整数，表示链表各节点的值。\n第三行包含一个整数 pos，表示环的入口位置（-1 表示无环）。",
        "output_format": "输出 true 或 false。",
        "constraints": "链表中节点的数目范围是 [0, 10^4]\n-10^5 <= Node.val <= 10^5\npos 为 -1 或者链表中的一个有效索引",
        "sample_input": json.dumps(["4\n3 2 0 -4\n1", "2\n1 2\n-1"]),
        "sample_output": json.dumps(["true", "false"]),
        "hint": "使用快慢指针（Floyd 判环算法）。快指针每次走两步，慢指针每次走一步，如果相遇则有环。",
        "time_limit": 1000,
        "memory_limit": 256,
        "difficulty": "easy",
        "tags": "链表,双指针",
    },
    {
        "display_id": "1022",
        "title": "最小栈",
        "description": "设计一个支持 push、pop、top 操作，并能在常数时间内检索到最小元素的栈。\n\n实现 MinStack 类：\n- MinStack() 初始化堆栈对象。\n- void push(int val) 将元素val推入堆栈。\n- void pop() 删除堆栈顶部的元素。\n- int top() 获取堆栈顶部的元素。\n- int getMin() 获取堆栈中的最小元素。",
        "input_format": "第一行包含一个整数 n，表示操作数量。\n接下来 n 行，每行一个操作：PUSH x、POP、TOP、GETMIN。",
        "output_format": "对于每个 TOP 和 GETMIN 操作，输出结果。",
        "constraints": "-2^31 <= val <= 2^31 - 1\npop、top 和 getMin 操作总是在非空的栈上调用\npush, pop, top, and getMin 最多被调用 3 * 10^4 次",
        "sample_input": json.dumps(["7\nPUSH -2\nPUSH 0\nPUSH -3\nGETMIN\nPOP\nTOP\nGETMIN"]),
        "sample_output": json.dumps(["-3\n0\n-2"]),
        "hint": "使用两个栈：一个普通栈和一个辅助最小栈。每次 push 时，最小栈同时记录当前最小值。",
        "time_limit": 1000,
        "memory_limit": 256,
        "difficulty": "medium",
        "tags": "栈,设计",
    },
    {
        "display_id": "1023",
        "title": "字符串的排列",
        "description": "给你两个字符串 s1 和 s2，写一个函数来判断 s2 是否包含 s1 的排列。\n\n换句话说，第一个字符串的排列之一是第二个字符串的子串。",
        "input_format": "第一行一个字符串 s1。\n第二行一个字符串 s2。",
        "output_format": "输出 true 或 false。",
        "constraints": "1 <= s1.length, s2.length <= 10^4\ns1 和 s2 仅包含小写字母",
        "sample_input": json.dumps(["ab", "eidbaooo", "ab", "eidboaoo"]),
        "sample_output": json.dumps(["true", "false"]),
        "hint": "使用滑动窗口和字符计数。窗口大小固定为 s1 的长度，比较窗口内字符计数是否与 s1 相同。",
        "time_limit": 1000,
        "memory_limit": 256,
        "difficulty": "medium",
        "tags": "滑动窗口,字符串",
    },
    {
        "display_id": "1024",
        "title": "买卖股票的最佳时机",
        "description": "给定一个数组 prices，它的第 i 个元素 prices[i] 表示一支给定股票第 i 天的价格。\n\n你只能选择某一天买入这只股票，并选择在未来的某一个不同的日子卖出该股票。设计一个算法来计算你所能获取的最大利润。\n\n如果你不能获取任何利润，返回 0。",
        "input_format": "第一行包含一个整数 n。\n第二行包含 n 个整数，表示每天的股票价格。",
        "output_format": "输出最大利润。",
        "constraints": "1 <= prices.length <= 10^5\n0 <= prices[i] <= 10^4",
        "sample_input": json.dumps(["6\n7 1 5 3 6 4", "5\n7 6 4 3 1"]),
        "sample_output": json.dumps(["5", "0"]),
        "hint": "遍历数组，维护当前最小价格 minPrice 和最大利润 maxProfit。每天更新 minPrice = min(minPrice, price)，maxProfit = max(maxProfit, price - minPrice)。",
        "time_limit": 1000,
        "memory_limit": 256,
        "difficulty": "easy",
        "tags": "数组,动态规划",
    },
    {
        "display_id": "1025",
        "title": "二叉树的最大深度",
        "description": "给定一个二叉树 root，返回其最大深度。\n\n二叉树的最大深度是指从根节点到最远叶子节点的最长路径上的节点数。",
        "input_format": "第一行包含一个整数 n，表示节点数。\n第二行包含 n 个整数（-1 表示空节点），按层序给出二叉树。",
        "output_format": "输出最大深度。",
        "constraints": "树中节点的数目范围 [0, 10^4]\n-100 <= Node.val <= 100",
        "sample_input": json.dumps(["7\n3 9 20 -1 -1 15 7", "1\n1"]),
        "sample_output": json.dumps(["3", "1"]),
        "hint": "递归：maxDepth(root) = 1 + max(maxDepth(root.left), maxDepth(root.right))。",
        "time_limit": 1000,
        "memory_limit": 256,
        "difficulty": "easy",
        "tags": "树,递归,深度优先搜索",
    },
    {
        "display_id": "1026",
        "title": "单词搜索",
        "description": "给定一个 m x n 二维字符网格 board 和一个字符串单词 word。如果 word 存在于网格中，返回 true；否则，返回 false。\n\n单词必须按照字母顺序，通过相邻的单元格内的字母组成，所谓「相邻」单元格是那些水平相邻或垂直相邻的单元格。同一个单元格内的字母不允许被重复使用。",
        "input_format": "第一行两个整数 m 和 n。\n接下来 m 行，每行 n 个字符。\n最后一行一个字符串 word。",
        "output_format": "输出 true 或 false。",
        "constraints": "1 <= m, n <= 6\n1 <= word.length <= 15\nboard 和 word 仅由大小写英文字母组成",
        "sample_input": json.dumps(["3 4\nA B C E\nS F C S\nA D E E\nABCCED"]),
        "sample_output": json.dumps(["true"]),
        "hint": "回溯 + DFS。从每个格子出发，尝试四个方向搜索 word 的下一个字符，用 visited 数组标记已访问的格子。",
        "time_limit": 2000,
        "memory_limit": 256,
        "difficulty": "medium",
        "tags": "回溯,深度优先搜索,矩阵",
    },
    {
        "display_id": "1027",
        "title": "旋转图像",
        "description": "给定一个 n × n 的二维矩阵 matrix 表示一个图像。请你将图像顺时针旋转 90 度。\n\n你必须在原地旋转图像，这意味着你需要直接修改输入的二维矩阵。",
        "input_format": "第一行包含一个整数 n。\n接下来 n 行，每行 n 个整数。",
        "output_format": "输出旋转后的矩阵，每行空格分隔。",
        "constraints": "n == matrix.length == matrix[i].length\n1 <= n <= 20\n-1000 <= matrix[i][j] <= 1000",
        "sample_input": json.dumps(["3\n1 2 3\n4 5 6\n7 8 9"]),
        "sample_output": json.dumps(["7 4 1\n8 5 2\n9 6 3"]),
        "hint": "先沿对角线翻转（转置），再沿垂直中线翻转（每行逆序）。",
        "time_limit": 1000,
        "memory_limit": 256,
        "difficulty": "medium",
        "tags": "数组,矩阵",
    },
    {
        "display_id": "1028",
        "title": "N皇后",
        "description": "按照国际象棋的规则，皇后可以攻击与之处在同一行或同一列或同一斜线上的棋子。\n\nn 皇后问题研究的是如何将 n 个皇后放置在 n×n 的棋盘上，并且使皇后彼此之间不能相互攻击。\n\n给你一个整数 n，返回所有不同的 n 皇后问题的解决方案。",
        "input_format": "一行一个整数 n。",
        "output_format": "每个方案用 n 行输出，每行 n 个字符（'Q' 表示皇后，'.' 表示空位）。方案之间空一行。按字典序输出。",
        "constraints": "1 <= n <= 9",
        "sample_input": json.dumps(["4"]),
        "sample_output": json.dumps([".Q..\n...Q\nQ...\n..Q.\n\n..Q.\nQ...\n...Q\n.Q.."]),
        "hint": "经典回溯。逐行放置皇后，用三个集合记录列、主对角线、副对角线的占用情况。",
        "time_limit": 2000,
        "memory_limit": 256,
        "difficulty": "hard",
        "tags": "回溯,递归",
    },
    {
        "display_id": "1029",
        "title": "删除链表的倒数第N个结点",
        "description": "给你一个链表，删除链表的倒数第 n 个结点，并且返回链表的头结点。",
        "input_format": "第一行包含一个整数 m，表示链表节点数。\n第二行包含 m 个整数，表示链表各节点的值。\n第三行包含一个整数 n。",
        "output_format": "输出删除节点后的链表，空格分隔。",
        "constraints": "链表中结点的数目为 sz\n1 <= sz <= 30\n1 <= n <= sz",
        "sample_input": json.dumps(["5\n1 2 3 4 5\n2", "1\n1\n1"]),
        "sample_output": json.dumps(["1 2 3 5", ""]),
        "hint": "使用快慢指针。快指针先走 n 步，然后快慢指针同时移动，快指针到达末尾时慢指针的下一个就是要删除的节点。",
        "time_limit": 1000,
        "memory_limit": 256,
        "difficulty": "medium",
        "tags": "链表,双指针",
    },
    {
        "display_id": "1030",
        "title": "柱状图中最大的矩形",
        "description": "给定 n 个非负整数，用来表示柱状图中各个柱子的高度。每个柱子彼此相邻，且宽度为 1。\n\n求在该柱状图中，能够勾勒出来的矩形的最大面积。",
        "input_format": "第一行包含一个整数 n。\n第二行包含 n 个非负整数，表示每个柱子的高度。",
        "output_format": "输出最大矩形面积。",
        "constraints": "1 <= n <= 10^5\n0 <= heights[i] <= 10^4",
        "sample_input": json.dumps(["6\n2 1 5 6 2 3", "2\n2 4"]),
        "sample_output": json.dumps(["10", "4"]),
        "hint": "使用单调递增栈。对于每根柱子，找到其左边和右边第一个比它矮的柱子，计算以该柱子为高的最大矩形面积。",
        "time_limit": 2000,
        "memory_limit": 256,
        "difficulty": "hard",
        "tags": "单调栈,数组",
    },
]


async def init_seed_problems(db: AsyncSession) -> None:
    """初始化种子题目数据"""
    # 检查是否已有数据
    stmt = select(func.count()).select_from(Problem)
    count = (await db.execute(stmt)).scalar_one()
    if count > 0:
        return

    for data in SEED_PROBLEMS:
        problem = Problem(**data)
        db.add(problem)

    await db.commit()
