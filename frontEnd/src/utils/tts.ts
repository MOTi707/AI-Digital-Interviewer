/**
 * TTS 工具模块（流式句子队列版）
 * - 支持句子级流水线：AI 边生成边朗读，无需等全部文字完成
 * - 优先 Edge TTS 后端，降级到 Web Speech API
 * - 预取机制：句子入队后立即发起 TTS 请求，播放完一句自动接下一句
 */

const API_BASE = 'http://localhost:8000'

// ── 句子队列状态 ──

interface QueueItem {
  text: string
  audioPromise: Promise<HTMLAudioElement | null>  // 预取的音频
}

let queue: QueueItem[] = []
let isPlaying = false
let currentAudio: HTMLAudioElement | null = null
let useEdgeTTS = true   // 是否使用 Edge TTS（失败时自动降级）
let onSpeakStart: (() => void) | null = null
let onSpeakEnd: (() => void) | null = null

// ── Edge TTS 后端（单句） ──

/**
 * 请求后端生成单句语音，返回 Audio 元素（预取）
 * 边下载边解码，不等完整响应
 */
function fetchSentenceAudio(text: string): Promise<HTMLAudioElement | null> {
  return fetch(`${API_BASE}/api/tts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  })
    .then(async (res) => {
      if (!res.ok) throw new Error(`TTS API error: ${res.status}`)

      // 用 ReadableStream 收集 blob（流式下载）
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const audio = new Audio(url)

      // 预加载
      audio.preload = 'auto'
      audio.load()

      // 播放结束后释放
      audio.onended = () => URL.revokeObjectURL(url)

      return audio
    })
    .catch(() => null)
}

// ── Web Speech API 降级 ──

let cachedVoice: SpeechSynthesisVoice | null = null
let voicesLoaded = false

function warmUpVoices(): Promise<void> {
  return new Promise((resolve) => {
    if (voicesLoaded || speechSynthesis.getVoices().length > 0) {
      voicesLoaded = true
      resolve()
      return
    }
    const handler = () => {
      voicesLoaded = true
      speechSynthesis.removeEventListener('voiceschanged', handler)
      resolve()
    }
    speechSynthesis.addEventListener('voiceschanged', handler)
    setTimeout(() => {
      voicesLoaded = true
      speechSynthesis.removeEventListener('voiceschanged', handler)
      resolve()
    }, 2000)
  })
}

function selectBestVoice(): SpeechSynthesisVoice | null {
  if (cachedVoice) return cachedVoice
  const voices = speechSynthesis.getVoices()
  const priority = ['Xiaoxiao', 'Yaoyao', 'Huihui', 'Kangkang']
  for (const name of priority) {
    const v = voices.find(v => v.lang.startsWith('zh') && v.name.includes(name))
    if (v) { cachedVoice = v; return v }
  }
  const zhVoice = voices.find(v => v.lang.startsWith('zh'))
  if (zhVoice) { cachedVoice = zhVoice; return zhVoice }
  return null
}

function speakSentenceWebSpeech(text: string): Promise<void> {
  return new Promise((resolve) => {
    if (!window.speechSynthesis) { resolve(); return }
    speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'zh-CN'
    utterance.rate = 0.95
    utterance.pitch = 1.15
    utterance.volume = 1.0
    const voice = selectBestVoice()
    if (voice) utterance.voice = voice
    utterance.onend = () => resolve()
    utterance.onerror = () => resolve()
    speechSynthesis.speak(utterance)
  })
}

// ── 队列播放引擎 ──

/**
 * 播放队列中的下一句（递归链式调用）
 */
async function playNext() {
  if (queue.length === 0) {
    isPlaying = false
    onSpeakEnd?.()
    return
  }

  const item = queue.shift()!
  if (!isPlaying) return  // 被 stopQueue 中断

  if (!onSpeakStart) {
    // 只触发一次 onStart（第一句开始时）
  }

  if (useEdgeTTS) {
    const audio = await item.audioPromise
    if (!isPlaying) return  // 被中断

    if (audio) {
      currentAudio = audio
      await new Promise<void>((resolve) => {
        audio.onended = () => {
          URL.revokeObjectURL(audio.src)
          currentAudio = null
          resolve()
        }
        audio.onerror = () => {
          currentAudio = null
          resolve()
        }
        audio.play().catch(() => {
          currentAudio = null
          resolve()
        })
      })
    } else {
      // Edge TTS 失败，降级到 Web Speech
      useEdgeTTS = false
      console.warn('Edge TTS 不可用，降级到 Web Speech API')
      await speakSentenceWebSpeech(item.text)
    }
  } else {
    await speakSentenceWebSpeech(item.text)
  }

  if (isPlaying) {
    await playNext()
  }
}

// ── 公共接口 ──

/**
 * 将一句文本加入 TTS 队列
 * - 立即发起 TTS 预取请求（不等播放）
 * - 播放引擎自动链式播放
 *
 * @param text  单句文本
 * @param onStart  首次开始朗读的回调（仅第一句触发）
 * @param onEnd    全部朗读完成的回调
 */
export function enqueueSentence(
  text: string,
  onStart?: () => void,
  onEnd?: () => void,
): void {
  if (onStart) onSpeakStart = onStart
  if (onEnd) onSpeakEnd = onEnd

  // 空文本只触发回调，不入队音频
  if (!text.trim()) {
    if (!isPlaying) {
      // 当前无播放中，直接触发 onEnd
      onSpeakEnd?.()
    }
    // 如果正在播放，onSpeakEnd 会在队列排空时由 playNext 触发
    return
  }

  // 立即发起预取（不等播放到这一句）
  const audioPromise = useEdgeTTS ? fetchSentenceAudio(text) : Promise.resolve(null)

  queue.push({ text, audioPromise })

  // 触发 onStart（第一句）
  if (!isPlaying) {
    isPlaying = true
    onSpeakStart?.()
    playNext()
  }
}

/**
 * 一次性朗读完整文本（兼容旧接口）
 * 按句子拆分后加入队列
 */
export async function speakText(
  text: string,
  onStart: () => void,
  onEnd: () => void,
): Promise<void> {
  await warmUpVoices()
  stopQueue()

  const sentences = splitSentences(text)
  if (sentences.length === 0) { onEnd(); return }

  sentences.forEach((s, i) => {
    enqueueSentence(
      s,
      i === 0 ? onStart : undefined,
      i === sentences.length - 1 ? onEnd : undefined,
    )
  })
}

/**
 * 停止当前朗读并清空队列
 */
export function stopQueue(): void {
  isPlaying = false
  queue = []
  if (currentAudio) {
    currentAudio.pause()
    currentAudio.currentTime = 0
    currentAudio = null
  }
  if (window.speechSynthesis) {
    speechSynthesis.cancel()
  }
  onSpeakStart = null
  onSpeakEnd = null
}

/**
 * 兼容旧接口：停止朗读
 */
export function stopSpeaking(): void {
  stopQueue()
}

// ── 工具函数 ──

/**
 * 按中文/英文标点拆分句子
 * 保留标点符号在句尾（TTS 朗读更自然）
 */
export function splitSentences(text: string): string[] {
  // 按中英文句子标点拆分，保留标点
  const parts = text.match(/[^。！？；\n.!?;]+[。！？；\n.!?;]?/g) || [text]
  return parts
    .map(s => s.trim())
    .filter(s => s.length > 0)
}

/**
 * 重置 TTS 引擎状态（切换后端时使用）
 */
export function resetTTSEngine(): void {
  useEdgeTTS = true
  stopQueue()
}
