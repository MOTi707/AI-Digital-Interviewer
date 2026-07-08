<template>
  <div class="flex flex-col flex-1 min-h-0">
    <!-- AI面试标题 -->
    <div class="mb-4 flex items-center justify-between shrink-0">
      <div>
        <h2 class="font-black text-xl">{{ round === 'ai_voice_3' ? '三面·AI面试' : '四面·综合面试' }}</h2>
        <p class="font-sans text-xs text-gray-600 mt-1">
          {{ round === 'ai_voice_3' ? '个人表达、行业趋势、抗压能力、职业规划' : '价值观、薪资谈判、文化契合' }}
        </p>
      </div>
      <div class="border-2 border-black px-3 py-1 font-black text-xs"
        :class="round === 'ai_voice_3' ? 'bg-[#8338ec] text-white' : 'bg-[#22c55e] text-white'">
        对话 {{ turnCount }} / {{ maxTurns }}
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-5 gap-4 flex-1 min-h-0">
      <!-- 左侧：数字人面试官 -->
      <div class="lg:col-span-2 border-4 border-black bg-white shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-5 flex flex-col items-center min-h-0 overflow-hidden">
        <InterviewAvatar ref="avatarRef" :speaking="isSpeaking" :avatar-state="avatarState" :input-focused="isInputFocused" />
        <div class="mt-4 font-black text-lg">AI面试官</div>
        <div class="mt-1 text-sm font-sans text-gray-500">
          {{ round === 'ai_voice_3' ? 'HR面试官' : '高管面试官' }}
        </div>

        <!-- TTS 控制 + 模型切换 -->
        <div class="mt-4 flex gap-2 items-center h-[38px]">
          <button
            class="border-2 border-black px-4 py-2 text-sm font-black transition-all duration-200 hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]"
            :class="isEku ? 'bg-[#ff006e] text-white' : 'bg-[#fef9ef]'"
            @click="toggleModel"
          >
            🎭 模型切换
          </button>
          <button
            class="border-2 border-black px-4 py-2 text-sm font-black bg-[#fef9ef] hover:bg-[#ffbe0b] transition-colors"
            :style="{ visibility: (lastAIResponse && !isSpeaking) ? 'visible' : 'hidden' }"
            @click="speakText(lastAIResponse)"
          >
            🔊 重新朗读
          </button>
        </div>
      </div>

      <!-- 右侧：对话区域 -->
      <div class="lg:col-span-3 border-4 border-black bg-white shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-5 flex flex-col flex-1 min-h-0 overflow-hidden">
        <!-- 对话消息列表 -->
        <div class="flex-1 overflow-y-auto space-y-3 mb-4">
          <div
            v-for="(msg, idx) in messages"
            :key="idx"
            :class="[
              'p-3 border-2 border-black text-sm font-sans',
              msg.role === 'interviewer'
                ? 'bg-[#fef9ef] mr-8'
                : 'bg-[#3a86ff]/10 ml-8 border-[#3a86ff]/30'
            ]"
          >
            <div class="font-black text-xs mb-1" :class="msg.role === 'interviewer' ? 'text-[#ff006e]' : 'text-[#3a86ff]'">
              {{ msg.role === 'interviewer' ? '🎤 面试官' : '🙋 候选人' }}
            </div>
            <p class="whitespace-pre-wrap leading-relaxed">{{ msg.content }}</p>
          </div>

          <!-- AI正在输入 -->
          <div v-if="aiTyping" class="p-3 border-2 border-black bg-[#fef9ef] mr-8">
            <div class="font-black text-xs mb-1 text-[#ff006e]">🎤 面试官</div>
            <p class="whitespace-pre-wrap leading-relaxed">{{ aiTypingText }}<span class="animate-pulse">|</span></p>
          </div>
        </div>

        <!-- 语音录制 / 文字输入 -->
        <div class="border-t-2 border-black pt-3">
          <!-- 语音识别状态 -->
          <div v-if="isRecording" class="flex items-center gap-2 mb-2">
            <div class="w-3 h-3 bg-red-500 animate-pulse" />
            <span class="font-sans text-xs text-red-600">正在录音...</span>
          </div>
          <div v-if="isTranscribing" class="flex items-center gap-2 mb-2">
            <div class="w-3 h-3 bg-blue-500 animate-pulse" />
            <span class="font-sans text-xs text-blue-600">识别中...</span>
          </div>

          <!-- 输入区域 -->
          <div class="flex gap-2">
            <textarea
              v-model="userInput"
              class="flex-1 border-4 border-black px-3 py-2 font-sans text-sm min-h-[80px] resize-none focus:outline-none focus:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]"
              placeholder="输入你的回答，或点击麦克风语音输入..."
              :disabled="aiTyping || turnComplete"
              @focus="isInputFocused = true"
              @blur="isInputFocused = false"
            />
          </div>

          <div class="flex gap-2 mt-2">
            <!-- 语音录制按钮 -->
            <button
              :disabled="aiTyping || turnComplete"
              :class="[
                'border-4 border-black px-4 py-2 font-black text-sm transition-all duration-200',
                isRecording
                  ? 'bg-red-500 text-white animate-pulse'
                  : 'bg-[#ffbe0b] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]'
              ]"
              @click="toggleRecording"
            >
              {{ isRecording ? '⏹ 停止' : '🎤 语音' }}
            </button>

            <!-- 发送按钮 -->
            <button
              :disabled="!userInput.trim() || aiTyping || turnComplete"
              class="flex-1 border-4 border-black bg-[#3a86ff] text-white font-black px-4 py-2 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all duration-200 disabled:opacity-50"
              @click="sendUserMessage"
            >
              发送回答
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 轮次完成 -->
    <div v-if="turnComplete" class="mt-4 border-4 border-black bg-white shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-6 text-center">
      <div class="text-4xl mb-3">🎤</div>
      <h3 class="font-black text-xl mb-2">{{ round === 'ai_voice_3' ? '三面完成！' : '全部面试完成！' }}</h3>
      <p class="font-sans text-sm text-gray-600 mb-4">共{{ turnCount }}轮对话</p>
      <button
        v-if="round === 'ai_voice_3'"
        class="border-4 border-black bg-[#ff006e] text-white font-black px-6 py-2 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all duration-200"
        @click="emit('roundComplete')"
      >
        进入四面 →
      </button>
      <button
        v-else
        class="border-4 border-black bg-[#22c55e] text-white font-black px-6 py-2 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all duration-200"
        @click="emit('roundComplete')"
      >
        查看评分报告 →
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onUnmounted, inject } from 'vue'
import { useInterviewStore, type QuestionItem, type AIChatMessage } from '@/stores/interview'
import InterviewAvatar from './InterviewAvatar.vue'
import { speakText as ttsSpeak, stopSpeaking as ttsStop, enqueueSentence, stopQueue } from '@/utils/tts'

type AvatarState = 'idle' | 'thinking' | 'satisfied' | 'probing'

const props = defineProps<{
  questions: QuestionItem[]
  sessionId: string
  round: string
}>()

const emit = defineEmits<{
  roundComplete: []
}>()

const showAlert = inject<(msg: string, icon?: string) => void>('showAlert', (msg) => alert(msg))

const store = useInterviewStore()
const messages = ref<AIChatMessage[]>([])
const userInput = ref('')
const aiTyping = ref(false)
const aiTypingText = ref('')
const isSpeaking = ref(false)
const lastAIResponse = ref('')
const turnCount = ref(0)
const maxTurns = 6
const turnComplete = ref(false)
const isRecording = ref(false)
const isTranscribing = ref(false)
const avatarState = ref<AvatarState>('idle')
const avatarRef = ref<InstanceType<typeof InterviewAvatar> | null>(null)
const isInputFocused = ref(false)
const isEku = ref(false)
let micStream: MediaStream | null = null
let audioRecorder: MediaRecorder | null = null
let audioChunks: Blob[] = []
let questionStartTime = Date.now()
let aiChatController: AbortController | null = null  // 用于中止在途的 AI 流式请求

// 过滤AI回复中的画外音描述，如（微笑）(点头)等
function stripStageDirections(text: string): string {
  return text
    .replace(/[（(][^）)]{0,10}[）)]/g, (match) => {
      // 保留有意义的括号内容（如举例、引用），去掉动作/表情描述
      const inner = match.slice(1, -1)
      const actionWords = ['微笑', '笑', '点头', '摇头', '思考', '沉默', '叹气', '皱眉', '惊讶', '满意', '点头示意', '微笑点头', '若有所思', '点头微笑', '笑着', '叹了口气', '点头表示', '点头说', '笑着说', '皱眉说', '点头继续', '点头鼓励', '微笑说', '点头回应']
      if (actionWords.some(w => inner.includes(w))) return ''
      return match
    })
    .replace(/\s{2,}/g, ' ')
    .trim()
}

// ── 模型切换 ──
function toggleModel() {
  isEku.value = !isEku.value
  const url = isEku.value ? '/models/Eku.vrm' : '/models/avatar.vrm'
  avatarRef.value?.switchModel(url)
}

// 去除括号内动作描述（微笑）(点头)等，用于TTS朗读前的清理
function stripStageDirectionsForTTS(text: string): string {
  return text
    .replace(/[（(][^）)]*?[）)]/g, (match) => {
      const inner = match.slice(1, -1)
      const actionWords = ['微笑', '笑', '点头', '摇头', '思考', '沉默', '叹气', '皱眉', '惊讶', '满意', '点头示意', '微笑点头', '若有所思', '点头微笑', '笑着', '叹了口气', '点头表示', '点头说', '笑着说', '皱眉说', '点头继续', '点头鼓励', '微笑说', '点头回应']
      if (actionWords.some(w => inner.includes(w))) return ''
      return match
    })
    .replace(/\s{2,}/g, ' ')
    .trim()
}

// ── TTS (流式句子队列 + Edge TTS + Web Speech API 降级) ──

function speakText(text: string) {
  ttsSpeak(
    text,
    () => { isSpeaking.value = true },
    () => {
      isSpeaking.value = false
      setTimeout(() => {
        if (!isSpeaking.value) {
          avatarState.value = 'idle'
        }
      }, 1000)
    },
  )
}

/**
 * 将 AI 流式输出中的一段句子加入 TTS 队列（边生成边朗读）
 * @param sentence 原始句子文本（可能含画外音括号）
 * @param isFirst 是否第一句（触发 onStart）
 * @param isLast  是否最后一句（触发 onEnd）
 */
function enqueueSentenceForTTS(sentence: string, isFirst: boolean, isLast: boolean) {
  const cleaned = stripStageDirectionsForTTS(sentence)
  if (!cleaned) return

  enqueueSentence(
    cleaned,
    isFirst ? () => { isSpeaking.value = true } : undefined,
    isLast ? () => {
      isSpeaking.value = false
      setTimeout(() => {
        if (!isSpeaking.value) avatarState.value = 'idle'
      }, 1000)
    } : undefined,
  )
}

// ── ASR (MediaRecorder + 后端 Whisper) ─────────────────────────

function toggleRecording() {
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

async function startRecording() {
  console.log('[ASR] startRecording called')
  // 停止 TTS 朗读
  ttsStop()
  isSpeaking.value = false
  speechSynthesis.cancel()

  try {
    micStream = await navigator.mediaDevices.getUserMedia({ audio: true })
    console.log('[ASR] Got microphone stream')
  } catch (e) {
    console.error('[ASR] Microphone error:', e)
    showAlert('无法访问麦克风：' + (e as Error).message, '🎙️')
    return
  }

  const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
    ? 'audio/webm;codecs=opus'
    : 'audio/webm'
  audioRecorder = new MediaRecorder(micStream, { mimeType })
  audioChunks = []
  userInput.value = ''
  isRecording.value = true

  audioRecorder.ondataavailable = (e) => {
    if (e.data.size > 0) {
      audioChunks.push(e.data)
    }
  }

  audioRecorder.start(1000)  // 每1秒触发一次 ondataavailable
  console.log('[ASR] MediaRecorder started, state:', audioRecorder.state)
}

/** 将 webm 音频转换为 WAV 格式（16kHz 单声道 16-bit PCM） */
async function webmToWav(webmBlob: Blob): Promise<Blob> {
  const audioCtx = new AudioContext({ sampleRate: 16000 })
  const arrayBuffer = await webmBlob.arrayBuffer()
  const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer)
  await audioCtx.close()

  // 取第一个声道并下采样到 16kHz
  const sampleRate = audioBuffer.sampleRate
  const targetRate = 16000
  const ratio = sampleRate / targetRate
  const length = Math.round(audioBuffer.length / ratio)
  const output = new Float32Array(length)
  const channelData = audioBuffer.getChannelData(0)
  for (let i = 0; i < length; i++) {
    output[i] = channelData[Math.round(i * ratio)] || 0
  }

  // 转换为 16-bit PCM
  const pcm16 = new Int16Array(length)
  for (let i = 0; i < length; i++) {
    const s = Math.max(-1, Math.min(1, output[i]))
    pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF
  }

  // 构造 WAV 文件头
  const wavBuffer = new ArrayBuffer(44 + pcm16.byteLength)
  const view = new DataView(wavBuffer)
  const writeStr = (offset: number, str: string) => {
    for (let i = 0; i < str.length; i++) view.setUint8(offset + i, str.charCodeAt(i))
  }
  writeStr(0, 'RIFF')
  view.setUint32(4, 36 + pcm16.byteLength, true)
  writeStr(8, 'WAVE')
  writeStr(12, 'fmt ')
  view.setUint32(16, 16, true)        // chunk size
  view.setUint16(20, 1, true)          // PCM format
  view.setUint16(22, 1, true)          // mono
  view.setUint32(24, targetRate, true) // sample rate
  view.setUint32(28, targetRate * 2, true) // byte rate
  view.setUint16(32, 2, true)          // block align
  view.setUint16(34, 16, true)         // bits per sample
  writeStr(36, 'data')
  view.setUint32(40, pcm16.byteLength, true)
  new Int16Array(wavBuffer, 44).set(pcm16)

  return new Blob([wavBuffer], { type: 'audio/wav' })
}

async function sendAudioForTranscribe(chunks: Blob[]) {
  isTranscribing.value = true
  try {
    const webmBlob = new Blob(chunks, { type: 'audio/webm' })
    const wavBlob = await webmToWav(webmBlob)
    console.log('[ASR] Converted WAV size:', wavBlob.size, 'bytes')

    const formData = new FormData()
    formData.append('audio', wavBlob, 'speech.wav')

    const res = await fetch('http://localhost:8000/api/asr/transcribe', {
      method: 'POST',
      body: formData,
    })
    console.log('[ASR] Response status:', res.status)
    if (!res.ok) {
      const errText = await res.text()
      console.error('[ASR] Server error:', errText)
      return
    }

    const data = await res.json()
    console.log('[ASR] Transcription result:', JSON.stringify(data))
    if (data.text) {
      userInput.value = data.text
      console.log('[ASR] Final text:', data.text)
    }
  } catch (e) {
    console.error('ASR transcribe error:', e)
  } finally {
    isTranscribing.value = false
  }
}

/** 卸载后端 ASR 模型，释放内存 */
async function unloadAsrModel() {
  try {
    await fetch('http://localhost:8000/api/asr/model', { method: 'DELETE' })
    console.log('[ASR] Model unloaded')
  } catch (e) {
    console.error('[ASR] Failed to unload model:', e)
  }
}

function stopRecording() {
  if (audioRecorder && audioRecorder.state !== 'inactive') {
    audioRecorder.onstop = async () => {
      if (audioChunks.length > 0) {
        const chunks = [...audioChunks]
        audioChunks = []
        await sendAudioForTranscribe(chunks)
      }
      // 录音结束后卸载 ASR 模型，释放内存
      unloadAsrModel()
    }
    audioRecorder.stop()
  }
  if (micStream) {
    micStream.getTracks().forEach(t => t.stop())
    micStream = null
  }
  isRecording.value = false
}

// ── 发送消息 ──────────────────────────────────────────────

async function sendUserMessage() {
  const text = userInput.value.trim()
  if (!text || aiTyping.value || turnComplete.value) return

  // 停止语音录制
  if (isRecording.value) stopRecording()

  // 添加用户消息
  messages.value.push({ role: 'candidate', content: text })
  userInput.value = ''

  // 用户发送回答后 → 面试官满意 + 微笑
  avatarState.value = 'satisfied'
  avatarRef.value?.setMood('happy', 2000)

  // 提交评分
  const duration = Math.floor((Date.now() - questionStartTime) / 1000)
  try {
    await store.submitAnswer(props.sessionId, `ai_${props.round}_${turnCount.value}`, text, duration)
  } catch (e) {
    console.error('提交答案失败:', e)
  }

  turnCount.value++
  questionStartTime = Date.now()

  // 检查是否达到最大轮次
  if (turnCount.value >= maxTurns) {
    turnComplete.value = true
    return
  }

  // 发送AI对话
  await fetchAIResponse()
}

async function fetchAIResponse() {
  aiTyping.value = true
  aiTypingText.value = ''

  // AI正在生成 → 面试官思考中
  avatarState.value = 'thinking'

  // 清空上一轮的 TTS 队列
  stopQueue()
  isSpeaking.value = false

  const chatMessages = messages.value.map(m => ({
    role: m.role === 'interviewer' ? 'assistant' : 'user',
    content: m.content,
  }))

  // ── 句子级流式 TTS 追踪 ──
  // 每当 AI 流式文字累积到完整句子（以。！？；等结尾），立即入队 TTS
  let ttsScanPos = 0          // 已处理到的字符位置
  let isFirstSentence = true  // 标记第一句（用于触发 onStart）
  const SENTENCE_END = /[。！？；\n.!?;]/

  try {
    // 创建 AbortController，用于中止流式请求
    aiChatController = new AbortController()

    const fullText = await store.sendAIChat(
      props.sessionId,
      chatMessages,
      props.round,
      (text: string) => {
        aiTypingText.value = text

        // 从上次处理位置开始扫描新到达的字符
        let pos = ttsScanPos
        while (pos < text.length) {
          if (SENTENCE_END.test(text[pos])) {
            // 检查是否有未闭合的括号（画外音可能跨句子）
            const segment = text.slice(ttsScanPos, pos + 1)
            const openCount = (segment.match(/[（(]/g) || []).length
            const closeCount = (segment.match(/[）)]/g) || []).length
            if (openCount > closeCount) {
              // 括号未闭合，等更多文字到达
              pos++
              continue
            }

            // 完整句子，入队 TTS（边生成边朗读）
            const sentence = segment.trim()
            if (sentence) {
              enqueueSentenceForTTS(sentence, isFirstSentence, false)
              isFirstSentence = false
            }
            ttsScanPos = pos + 1
          }
          pos++
        }
      },
      aiChatController.signal,
    )

    // 处理末尾残余文字（最后一个句子可能没有以句号结尾）
    const cleanedFull = stripStageDirections(fullText)
    if (ttsScanPos < fullText.length) {
      const remainder = fullText.slice(ttsScanPos).trim()
      if (remainder) {
        enqueueSentenceForTTS(remainder, isFirstSentence, true)
        isFirstSentence = false
      }
    }

    // 如果只有一句且以标点结尾（已经在循环里入队了），补上 onEnd
    if (!isFirstSentence) {
      // 最后一句的 onEnd 已在 enqueueSentenceForTTS 里通过 isLast 触发
      // 但如果最后一句是在循环里入队的（非 remainder），需要补上结束回调
      // → 用一个空句子带 onEnd 来确保结束回调被触发
      enqueueSentence('', undefined, () => {
        isSpeaking.value = false
        setTimeout(() => {
          if (!isSpeaking.value) avatarState.value = 'idle'
        }, 1000)
      })
    }

    aiTyping.value = false
    lastAIResponse.value = cleanedFull
    messages.value.push({ role: 'interviewer', content: cleanedFull })

    // AI回复完成 → 追问状态 + 惊讶表情
    avatarState.value = 'probing'
    avatarRef.value?.setMood('surprised', 1500)

    // 自动滚动到底部
    await nextTick()
    const chatContainer = document.querySelector('.overflow-y-auto')
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight
    }
  } catch (e) {
    aiTyping.value = false
    aiChatController = null
    avatarState.value = 'idle'
    // 如果是被主动中止的，不显示错误消息
    if ((e as Error).name === 'AbortError') return
    messages.value.push({ role: 'interviewer', content: `抱歉，面试官暂时无法回应：${(e as Error).message}` })
  }
}

// ── 初始化：显示第一个AI问题 ──────────────────────────────

watch(() => props.questions, (newQ) => {
  if (newQ.length > 0) {
    messages.value = []
    turnCount.value = 0
    turnComplete.value = false
    userInput.value = ''

    const firstQ = newQ[0]
    const aiText = (firstQ.content as any).text || '你好，请开始你的面试。'
    messages.value.push({ role: 'interviewer', content: aiText })
    lastAIResponse.value = aiText
    questionStartTime = Date.now()

    // TTS朗读第一个问题
    setTimeout(() => speakText(aiText), 500)
  }
}, { immediate: true })

onUnmounted(() => {
  // 中止在途的 AI 流式请求
  aiChatController?.abort()
  aiChatController = null
  if (isRecording.value) stopRecording()
  ttsStop()
})

// ── 监听面试状态变化：外部中止时立即停止一切 ──
watch(() => store.currentSession?.status, (newStatus) => {
  if (newStatus && newStatus !== 'in_progress') {
    // 面试被中止（无论是手动还是切屏），立即取消在途请求和 TTS
    aiChatController?.abort()
    aiChatController = null
    stopQueue()
    isSpeaking.value = false
    aiTyping.value = false
    if (isRecording.value) stopRecording()
  }
})
</script>
