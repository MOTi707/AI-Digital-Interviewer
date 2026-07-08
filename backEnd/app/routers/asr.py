"""ASR 语音识别路由 - 使用讯飞语音听写 WebSocket API（极速优化版）"""

import asyncio
import base64
import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone
from urllib.parse import urlencode

import websockets
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

from app.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/asr", tags=["asr"])

IFLYTEK_WS_URL = "wss://iat-api.xfyun.cn/v2/iat"
FRAME_SIZE = 1280  # 官方推荐帧大小（base64 后不超过 13000B）


def _build_auth_url(api_key: str, api_secret: str) -> str:
    """根据讯飞鉴权规则生成带签名的 WebSocket URL"""
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%a, %d %b %Y %H:%M:%S GMT")

    signature_origin = (
        f"host: iat-api.xfyun.cn\n"
        f"date: {date_str}\n"
        f"GET /v2/iat HTTP/1.1"
    )
    signature_sha = hmac.new(
        api_secret.encode("utf-8"),
        signature_origin.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    signature = base64.b64encode(signature_sha).decode("utf-8")

    authorization_origin = (
        f'api_key="{api_key}", '
        f'algorithm="hmac-sha256", '
        f'headers="host date request-line", '
        f'signature="{signature}"'
    )
    authorization = base64.b64encode(
        authorization_origin.encode("utf-8")
    ).decode("utf-8")

    params = {
        "authorization": authorization,
        "date": date_str,
        "host": "iat-api.xfyun.cn",
    }
    return f"{IFLYTEK_WS_URL}?{urlencode(params)}"


def _strip_wav_header(audio_bytes: bytes) -> bytes:
    """去除 WAV 文件头（44字节），返回纯 PCM 数据"""
    if audio_bytes[:4] == b"RIFF" and audio_bytes[8:12] == b"WAVE":
        return audio_bytes[44:]
    return audio_bytes


def _parse_result(result_json: dict) -> str:
    """从讯飞返回的 JSON 中提取识别文本"""
    try:
        code = result_json.get("code", -1)
        if code != 0:
            logger.error(f"iFlytek error code: {code}, message: {result_json.get('message', '')}")
            return ""

        data = result_json.get("data", {})
        result = data.get("result", {})
        ws_list = result.get("ws", [])

        text_parts = []
        for ws_item in ws_list:
            cw_list = ws_item.get("cw", [])
            for cw_item in cw_list:
                text_parts.append(cw_item.get("w", ""))

        return "".join(text_parts)
    except Exception as e:
        logger.error(f"Parse iFlytek result error: {e}")
        return ""


async def _transcribe_with_iflytek(audio_bytes: bytes) -> str:
    """通过讯飞 WebSocket API 识别音频（极速优化：无延迟批量发送）"""
    settings = get_settings()

    if not settings.iflytek_app_id or not settings.iflytek_api_key or not settings.iflytek_api_secret:
        raise ValueError("讯飞 ASR 未配置，请在 .env 中设置 IFLYTEK_APP_ID / IFLYTEK_API_KEY / IFLYTEK_API_SECRET")

    pcm_data = _strip_wav_header(audio_bytes)
    if len(pcm_data) < 100:
        return ""

    auth_url = _build_auth_url(settings.iflytek_api_key, settings.iflytek_api_secret)
    result_texts: dict[int, str] = {}
    finished = asyncio.Event()
    error_msg = None

    async def _receive_loop(ws):
        nonlocal error_msg
        try:
            async for raw_resp in ws:
                resp_json = json.loads(raw_resp)
                code = resp_json.get("code", -1)
                if code != 0:
                    error_msg = resp_json.get("message", f"错误码: {code}")
                    logger.error(f"[ASR] iFlytek error: {error_msg}")
                    finished.set()
                    return

                text = _parse_result(resp_json)
                if text:
                    sn = resp_json.get("data", {}).get("result", {}).get("sn", 0)
                    pgs = resp_json.get("data", {}).get("result", {}).get("pgs", "")
                    if pgs == "rpl":
                        rge = resp_json.get("data", {}).get("result", {}).get("rg", [])
                        if len(rge) == 2:
                            for old_sn in range(rge[0], rge[1] + 1):
                                result_texts.pop(old_sn, None)
                    result_texts[sn] = text

                status = resp_json.get("data", {}).get("status", -1)
                if status == 2:
                    finished.set()
                    return
        except websockets.ConnectionClosed:
            finished.set()
        except Exception as e:
            logger.error(f"[ASR] Receive loop error: {e}")
            error_msg = str(e)
            finished.set()

    async with websockets.connect(auth_url) as ws:
        recv_task = asyncio.create_task(_receive_loop(ws))

        # 第一帧：含公共参数 + 首帧音频
        first_audio = pcm_data[:FRAME_SIZE]
        first_frame = {
            "common": {"app_id": settings.iflytek_app_id},
            "business": {
                "language": "zh_cn",
                "domain": "iat",
                "accent": "mandarin",
                "eos": 5000,
            },
            "data": {
                "status": 0,
                "format": "audio/L16;rate=16000",
                "encoding": "raw",
                "audio": base64.b64encode(first_audio).decode("utf-8"),
            },
        }
        await ws.send(json.dumps(first_frame))

        # 极速发送所有后续帧（无 sleep，预录音无需模拟实时）
        offset = FRAME_SIZE
        while offset < len(pcm_data) and not finished.is_set():
            remaining = pcm_data[offset:offset + FRAME_SIZE]
            is_last = (offset + FRAME_SIZE >= len(pcm_data))
            frame = {
                "data": {
                    "status": 2 if is_last else 1,
                    "format": "audio/L16;rate=16000",
                    "encoding": "raw",
                    "audio": base64.b64encode(remaining).decode("utf-8"),
                },
            }
            await ws.send(json.dumps(frame))
            offset += FRAME_SIZE

        logger.info(f"[ASR] All {offset} bytes sent in {(offset // FRAME_SIZE) + 1} frames, waiting result...")

        # 等待识别完成
        try:
            await asyncio.wait_for(finished.wait(), timeout=15.0)
        except asyncio.TimeoutError:
            logger.warning("[ASR] Timed out waiting for result")
        finally:
            recv_task.cancel()

    if error_msg:
        raise RuntimeError(f"讯飞识别错误: {error_msg}")

    final_text = "".join(result_texts[k] for k in sorted(result_texts.keys()))
    logger.info(f"[ASR] Final transcription: '{final_text}'")
    return final_text


@router.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    """接收音频文件，返回识别文本"""
    audio_bytes = await audio.read()
    if not audio_bytes or len(audio_bytes) < 100:
        return JSONResponse(status_code=400, content={"error": "音频数据为空或太短"})

    try:
        text = await asyncio.wait_for(
            _transcribe_with_iflytek(audio_bytes),
            timeout=20.0,
        )
        return {"text": text}
    except asyncio.TimeoutError:
        logger.error("ASR transcription timed out")
        return JSONResponse(status_code=504, content={"error": "语音识别超时"})
    except ValueError as e:
        logger.error(f"ASR config error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
    except Exception as e:
        logger.error(f"ASR transcription error: {e}")
        return JSONResponse(status_code=500, content={"error": f"识别失败: {str(e)}"})


@router.delete("/model")
async def unload_model():
    """讯飞 API 无需管理本地模型，保留此端点以兼容前端调用"""
    return {"message": "讯飞在线识别无需卸载模型"}
