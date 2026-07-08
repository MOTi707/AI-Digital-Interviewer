"""
代码执行器 - 通过 subprocess 实际运行用户代码
支持语言: python3, c, cpp, java, javascript
安全策略: 关键词黑名单 + 危险模块拦截
"""
import asyncio
import logging
import os
import re
import shutil
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from app.config import get_settings

logger = logging.getLogger(__name__)

# ────────────────────────────────────────────────────────────
# 安全限制：危险关键词黑名单
# ────────────────────────────────────────────────────────────

# 通用危险关键词（跨语言适用）
_COMMON_DANGEROUS = [
    # Windows 系统命令
    r"\bformat\s+[a-zA-Z]:",          # format C:
    r"\bdel\s+/[fFsS]",                 # del /f /s
    r"\brmdir\s+/[sS]",                 # rmdir /s
    r"\bnet\s+user\b",                  # net user
    r"\bnetsh\b",                       # netsh (network config)
    r"\bschtasks\b",                    # scheduled tasks
    r"\bwmic\b",                        # WMI commands
    r"\breg\s+(delete|add)\b",         # reg delete / reg add
    r"\bshutdown\b",                    # shutdown command
    r"\brestart\b",                     # restart command
    r"\btaskkill\b",                    # taskkill
    r"\btskill\b",                      # tskill
]

# Python 危险模式
_PYTHON_DANGEROUS = [
    # 文件系统破坏
    r"\bos\.(remove|unlink|rmdir|removedirs|rename|renames)\b",
    r"\bos\.(system|popen|exec\w*|spawn\w*|startfile)\b",
    r"\bos\.(kill|abort)\b",
    r"\bos\.path\.(exists|isfile|isdir)\s*\(\s*['\"][A-Z]:\\",
    # shutil 危险操作
    r"\bshutil\.(rmtree|move|copy|copytree|disk_usage)\b",
    # subprocess / 进程
    r"\bsubprocess\b",
    r"\bPopen\b",
    # Windows 注册表
    r"\bwinreg\b",
    r"\b_reg\b",
    # 动态导入绕过
    r"\b__import__\b",
    r"\bimportlib\b",
    # ctypes 调用 Windows API
    r"\bctypes\b",
    r"\bwindll\b",
    r"\bcdll\b",
    # 网络 / socket 服务器
    r"\bsocket\.(socket|create_connection|gethostbyname)\b",
    r"\bhttp\.server\b",
    r"\bsocketserver\b",
    # 环境变量泄露
    r"\bos\.environ\b",
    r"\bos\.getenv\b",
    # eval / exec 动态代码
    r"\beval\s*\(",
    r"\bexec\s*\(",
    r"\bcompile\s*\(",
    # 路径遍历到系统目录
    r"['\"]C:\\Windows",
    r"['\"]C:\\Users\\",
    r"['\"]C:\\Program\s+Files",
    # open 写入系统路径
    r"open\s*\(\s*['\"][A-Z]:\\Windows",
    r"open\s*\(\s*['\"][A-Z]:\\Program",
]

# C/C++ 危险模式
_C_DANGEROUS = [
    r"\bsystem\s*\(",
    r"\bpopen\s*\(",
    r"\bexec[lv]?[pe]?\s*\(",
    r"\bWinExec\s*\(",
    r"\bShellExecute[A]?\s*\(",
    r"\bCreateProcess[A]?\s*\(",
    r"\bCreateRemoteThread\s*\(",
    r"\bWriteProcessMemory\s*\(",
    r"\bRegDeleteKey[A]?\s*\(",
    r"\bRegSetValue[A]?\s*\(",
    r"\bDeleteFile[A]?\s*\(",
    r"\bRemoveDirectory[A]?\s*\(",
    r"\bMoveFile[A]?\s*\(",
    r"\bCopyFile[A]?\s*\(",
    r"\bGetEnvironmentVariable\s*\(",
    r"\bSetEnvironmentVariable\s*\(",
    r'#\s*include\s*[<"]windows\.h[>"]',
    r'#\s*include\s*[<"]shellapi\.h[>"]',
    r'#\s*include\s*[<"]winreg\.h[>"]',
]

# Java 危险模式
_JAVA_DANGEROUS = [
    r"\bRuntime\.(getRuntime|exec)\b",
    r"\bProcessBuilder\b",
    r"\bjava\.lang\.Runtime\b",
    r"\bProcess\b",
    r"\bjava\.nio\.file\.Files\.(delete|move|copy|createFile|createDirectory)\b",
    r"\bjava\.io\.File\b.*\.(delete|renameTo)\b",
    r"\bDesktop\.(getDesktop|browse|open)\b",
    r"\bjava\.util\.prefs\.Preferences\b",
    r"\bSystem\.getenv\b",
    r"\bSystem\.getProperty\b",
    r"\bjava\.net\.(Socket|ServerSocket|URL)\b",
    r"\bjava\.lang\.reflect\b",
    r"\bClass\.forName\b",
]

# JavaScript/Node.js 危险模式
_JS_DANGEROUS = [
    r"\brequire\s*\(\s*['\"]child_process['\"]",
    r"\brequire\s*\(\s*['\"]fs['\"]",
    r"\brequire\s*\(\s*['\"]path['\"]",
    r"\brequire\s*\(\s*['\"]os['\"]",
    r"\brequire\s*\(\s*['\"]net['\"]",
    r"\brequire\s*\(\s*['\"]http['\"]",
    r"\brequire\s*\(\s*['\"]https['\"]",
    r"\brequire\s*\(\s*['\"]cluster['\"]",
    r"\brequire\s*\(\s*['\"]dgram['\"]",
    r"\bimport\s*\(\s*['\"]child_process['\"]",
    r"\bimport\s*\(\s*['\"]fs['\"]",
    r"\bimport\s*\(\s*['\"]node:",
    r"\bprocess\.(exit|kill|env|cwd|chdir)\b",
    r"\bglobal\b\s*\[",
    r"\beval\s*\(",
    r"\bnew\s+Function\s*\(",
]

# 每种语言的完整黑名单
_DANGEROUS_PATTERNS: dict[str, list[re.Pattern]] = {
    "python3": [re.compile(p, re.IGNORECASE) for p in _COMMON_DANGEROUS + _PYTHON_DANGEROUS],
    "c":       [re.compile(p, re.IGNORECASE) for p in _COMMON_DANGEROUS + _C_DANGEROUS],
    "cpp":     [re.compile(p, re.IGNORECASE) for p in _COMMON_DANGEROUS + _C_DANGEROUS],
    "java":    [re.compile(p, re.IGNORECASE) for p in _COMMON_DANGEROUS + _JAVA_DANGEROUS],
    "javascript": [re.compile(p, re.IGNORECASE) for p in _COMMON_DANGEROUS + _JS_DANGEROUS],
}


def _check_code_safety(code: str, language: str) -> str | None:
    """检查代码安全性，返回 None 表示安全，否则返回拒绝原因"""
    lang = LANG_MAP.get(language, language)
    patterns = _DANGEROUS_PATTERNS.get(lang, [])
    for pat in patterns:
        m = pat.search(code)
        if m:
            # 找到匹配的危险片段，提取上下文
            start = max(0, m.start() - 10)
            end = min(len(code), m.end() + 10)
            snippet = code[start:end].replace("\n", " ").strip()
            logger.warning("Code rejected [%s]: matched %s in '%s'", lang, pat.pattern, snippet)
            return f"代码包含禁止的操作: \"{snippet}\"（安全策略拦截）"
    return None

# 线程池用于执行子进程
_executor = ThreadPoolExecutor(max_workers=4)


def _resolve_bin(env_override: str | None, fallback_name: str) -> str:
    """解析编译器路径：优先使用 .env 配置，否则自动从 PATH 检测"""
    if env_override:
        return env_override
    detected = shutil.which(fallback_name)
    if detected:
        logger.debug("Auto-detected %s -> %s", fallback_name, detected)
        return detected
    logger.warning(
        "Compiler '%s' not found in PATH and not set in .env, using bare name", fallback_name
    )
    return fallback_name


def _get_bins() -> dict[str, str]:
    """从配置 + 自动检测获取所有编译器路径"""
    cfg = get_settings()
    return {
        "python": _resolve_bin(cfg.python_bin, "python"),
        "gcc": _resolve_bin(cfg.gcc_bin, "gcc"),
        "gpp": _resolve_bin(cfg.gpp_bin, "g++"),
        "java": _resolve_bin(cfg.java_bin, "java"),
        "javac": _resolve_bin(cfg.javac_bin, "javac"),
        "node": _resolve_bin(cfg.node_bin, "node"),
    }

# 语言映射（前端传来的 key -> 内部 key）
LANG_MAP = {
    "python3": "python3",
    "python": "python3",
    "c": "c",
    "cpp": "cpp",
    "java": "java",
    "javascript": "javascript",
}


@dataclass
class ExecuteResult:
    stdout: str
    stderr: str
    exit_code: int
    execution_time: int  # ms
    execution_memory: int  # KB (approx)
    status: str  # "success" | "compilation_error" | "runtime_error" | "time_limit_exceeded"


def _run_subprocess_sync(
    cmd: list[str],
    input_data: str,
    timeout_ms: int,
    cwd: str | None = None,
) -> tuple[str, str, int, float]:
    """同步运行子进程（在线程池中调用）"""
    timeout_sec = timeout_ms / 1000.0
    start = time.perf_counter()
    try:
        result = subprocess.run(
            cmd,
            input=input_data.encode("utf-8") if input_data else None,
            capture_output=True,
            timeout=timeout_sec,
            cwd=cwd,
        )
        elapsed = (time.perf_counter() - start) * 1000
        return (
            result.stdout.decode("utf-8", errors="replace"),
            result.stderr.decode("utf-8", errors="replace"),
            result.returncode,
            elapsed,
        )
    except subprocess.TimeoutExpired:
        elapsed = (time.perf_counter() - start) * 1000
        return ("", "Time Limit Exceeded", -1, elapsed)
    except Exception as e:
        elapsed = (time.perf_counter() - start) * 1000
        return ("", f"{type(e).__name__}: {e}", -1, elapsed)


async def _run_subprocess(
    cmd: list[str],
    input_data: str,
    timeout_ms: int,
    cwd: str | None = None,
) -> tuple[str, str, int, float]:
    """异步包装：在线程池中运行子进程"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _executor,
        _run_subprocess_sync,
        cmd,
        input_data,
        timeout_ms,
        cwd,
    )


async def execute_code(
    code: str,
    language: str,
    input_data: str = "",
    time_limit_ms: int = 2000,
) -> ExecuteResult:
    """执行用户代码并返回结果"""
    lang = LANG_MAP.get(language, language)

    # ── 安全检查：拦截危险关键词 ──
    safety_msg = _check_code_safety(code, language)
    if safety_msg:
        return ExecuteResult(
            stdout="",
            stderr=safety_msg,
            exit_code=-1,
            execution_time=0,
            execution_memory=0,
            status="compilation_error",
        )

    # 创建临时目录
    tmp_dir = tempfile.mkdtemp(prefix="oj_")

    try:
        if lang == "python3":
            return await _exec_python(code, input_data, time_limit_ms, tmp_dir)
        elif lang == "c":
            return await _exec_c(code, input_data, time_limit_ms, tmp_dir)
        elif lang == "cpp":
            return await _exec_cpp(code, input_data, time_limit_ms, tmp_dir)
        elif lang == "java":
            return await _exec_java(code, input_data, time_limit_ms, tmp_dir)
        elif lang == "javascript":
            return await _exec_javascript(code, input_data, time_limit_ms, tmp_dir)
        else:
            return ExecuteResult(
                stdout="",
                stderr=f"不支持的语言: {language}",
                exit_code=-1,
                execution_time=0,
                execution_memory=0,
                status="compilation_error",
            )
    finally:
        # 清理临时文件
        import shutil
        try:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception:
            pass


async def _exec_python(
    code: str, input_data: str, time_limit_ms: int, tmp_dir: str
) -> ExecuteResult:
    src = os.path.join(tmp_dir, "main.py")
    with open(src, "w", encoding="utf-8") as f:
        f.write(code)

    bins = _get_bins()
    stdout, stderr, rc, elapsed = await _run_subprocess(
        [bins["python"], src], input_data, time_limit_ms, cwd=tmp_dir
    )

    if rc == -1 and "Time Limit Exceeded" in stderr:
        return ExecuteResult("", stderr, -1, int(elapsed), 0, "time_limit_exceeded")
    if rc != 0:
        return ExecuteResult(stdout, stderr, rc, int(elapsed), 0, "runtime_error")
    return ExecuteResult(stdout, stderr, rc, int(elapsed), 0, "success")


async def _exec_c(
    code: str, input_data: str, time_limit_ms: int, tmp_dir: str
) -> ExecuteResult:
    src = os.path.join(tmp_dir, "main.c")
    exe = os.path.join(tmp_dir, "main.exe")
    with open(src, "w", encoding="utf-8") as f:
        f.write(code)

    bins = _get_bins()
    # 编译
    compile_stdout, compile_stderr, compile_rc, compile_time = await _run_subprocess(
        [bins["gcc"], src, "-o", exe, "-O2", "-lm"], "", 10000, cwd=tmp_dir
    )
    if compile_rc != 0:
        return ExecuteResult(
            "", compile_stderr, compile_rc, int(compile_time), 0, "compilation_error"
        )

    # 运行
    stdout, stderr, rc, elapsed = await _run_subprocess(
        [exe], input_data, time_limit_ms, cwd=tmp_dir
    )
    if rc == -1 and "Time Limit Exceeded" in stderr:
        return ExecuteResult("", stderr, -1, int(elapsed), 0, "time_limit_exceeded")
    if rc != 0:
        return ExecuteResult(stdout, stderr, rc, int(elapsed), 0, "runtime_error")
    return ExecuteResult(stdout, stderr, rc, int(elapsed), 0, "success")


async def _exec_cpp(
    code: str, input_data: str, time_limit_ms: int, tmp_dir: str
) -> ExecuteResult:
    src = os.path.join(tmp_dir, "main.cpp")
    exe = os.path.join(tmp_dir, "main.exe")
    with open(src, "w", encoding="utf-8") as f:
        f.write(code)

    bins = _get_bins()
    # 编译
    compile_stdout, compile_stderr, compile_rc, compile_time = await _run_subprocess(
        [bins["gpp"], src, "-o", exe, "-O2", "-lm"], "", 10000, cwd=tmp_dir
    )
    if compile_rc != 0:
        return ExecuteResult(
            "", compile_stderr, compile_rc, int(compile_time), 0, "compilation_error"
        )

    # 运行
    stdout, stderr, rc, elapsed = await _run_subprocess(
        [exe], input_data, time_limit_ms, cwd=tmp_dir
    )
    if rc == -1 and "Time Limit Exceeded" in stderr:
        return ExecuteResult("", stderr, -1, int(elapsed), 0, "time_limit_exceeded")
    if rc != 0:
        return ExecuteResult(stdout, stderr, rc, int(elapsed), 0, "runtime_error")
    return ExecuteResult(stdout, stderr, rc, int(elapsed), 0, "success")


async def _exec_java(
    code: str, input_data: str, time_limit_ms: int, tmp_dir: str
) -> ExecuteResult:
    src = os.path.join(tmp_dir, "Main.java")
    with open(src, "w", encoding="utf-8") as f:
        f.write(code)

    bins = _get_bins()
    # 编译（指定 UTF-8 编码，避免 Windows 默认 GBK 导致编译错误）
    compile_stdout, compile_stderr, compile_rc, compile_time = await _run_subprocess(
        [bins["javac"], "-encoding", "UTF-8", src], "", 15000, cwd=tmp_dir
    )
    if compile_rc != 0:
        return ExecuteResult(
            "", compile_stderr, compile_rc, int(compile_time), 0, "compilation_error"
        )

    # 运行
    stdout, stderr, rc, elapsed = await _run_subprocess(
        [bins["java"], "-cp", tmp_dir, "Main"], input_data, time_limit_ms, cwd=tmp_dir
    )
    if rc == -1 and "Time Limit Exceeded" in stderr:
        return ExecuteResult("", stderr, -1, int(elapsed), 0, "time_limit_exceeded")
    if rc != 0:
        return ExecuteResult(stdout, stderr, rc, int(elapsed), 0, "runtime_error")
    return ExecuteResult(stdout, stderr, rc, int(elapsed), 0, "success")


async def _exec_javascript(
    code: str, input_data: str, time_limit_ms: int, tmp_dir: str
) -> ExecuteResult:
    src = os.path.join(tmp_dir, "main.js")
    with open(src, "w", encoding="utf-8") as f:
        f.write(code)

    bins = _get_bins()
    stdout, stderr, rc, elapsed = await _run_subprocess(
        [bins["node"], src], input_data, time_limit_ms, cwd=tmp_dir
    )
    if rc == -1 and "Time Limit Exceeded" in stderr:
        return ExecuteResult("", stderr, -1, int(elapsed), 0, "time_limit_exceeded")
    if rc != 0:
        return ExecuteResult(stdout, stderr, rc, int(elapsed), 0, "runtime_error")
    return ExecuteResult(stdout, stderr, rc, int(elapsed), 0, "success")
