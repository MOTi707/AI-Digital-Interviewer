"""TTS 语音合成路由 - 使用 edge-tts 生成高质量中文语音（流式输出）"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import edge_tts

router = APIRouter(prefix="/api/tts", tags=["tts"])

# 面试官人设默认语音配置
DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"  # 温柔知性女声
DEFAULT_RATE = "-5%"    # 略慢，从容
DEFAULT_PITCH = "+5Hz"  # 略高，温柔
DEFAULT_VOLUME = "+0%"


class TTSRequest(BaseModel):
    text: str
    voice: str = DEFAULT_VOICE
    rate: str = DEFAULT_RATE
    pitch: str = DEFAULT_PITCH
    volume: str = DEFAULT_VOLUME


@router.post("")
async def text_to_speech(req: TTSRequest):
    """将文本转换为语音音频，流式返回 MP3 数据（边生成边发送）"""
    communicate = edge_tts.Communicate(
        text=req.text,
        voice=req.voice,
        rate=req.rate,
        volume=req.volume,
        pitch=req.pitch,
    )

    async def audio_stream():
        """逐块 yield 音频数据，不缓冲"""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]

    return StreamingResponse(
        audio_stream(),
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline; filename=tts.mp3"},
    )


@router.get("/voices")
async def list_voices():
    """列出所有可用的中文语音"""
    voices = await edge_tts.list_voices()
    zh_voices = [
        {"name": v["ShortName"], "gender": v["Gender"], "locale": v["Locale"]}
        for v in voices
        if v["Locale"].startswith("zh-")
    ]
    return {"voices": zh_voices}
