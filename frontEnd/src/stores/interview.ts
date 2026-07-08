import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// ── Types ──────────────────────────────────────────────────

export interface JobPosition {
  id: string
  title: string
  icon: string
  description: string
}

export interface JobCategory {
  category: string
  positions: JobPosition[]
}

export interface RoundProgress {
  round_key: string
  label: string
  status: 'pending' | 'active' | 'completed'
}

export interface InterviewSession {
  id: string
  job_category: string
  job_title: string
  current_round: string
  status: string
  cheat_count: number
  interview_mode: string
  target_round: string | null
  rounds_progress: RoundProgress[]
  started_at: string
}

export interface QuestionItem {
  id: string
  question_type: 'choice' | 'judgment' | 'code' | 'open_ended'
  content: Record<string, unknown>
  time_limit: number
}

export interface AnswerResponse {
  correct: boolean
  score: number
  feedback: string
  correct_answer: string | Record<string, unknown> | null
}

export interface AIChatMessage {
  role: 'interviewer' | 'candidate'
  content: string
}

export interface RadarData {
  professional: number
  logic: number
  communication: number
  match: number
}

export interface RoundDetail {
  round_key: string
  label: string
  score: number
  max_score: number
  answers: Record<string, unknown>[]
}

export interface InterviewReport {
  session_id: string
  job_category: string
  job_title: string
  total_score: number
  max_total: number
  grade: string
  radar: RadarData
  round_details: RoundDetail[]
  suggestions: string[]
  ai_analysis: string
  completed_at: string | null
  interview_mode: string
  target_round: string | null
}

export interface InterviewHistoryItem {
  id: string
  job_category: string
  job_title: string
  status: string
  total_score: number | null
  grade: string | null
  cheat_count: number
  interview_mode: string
  target_round: string | null
  started_at: string
  completed_at: string | null
}

// ── API Client ─────────────────────────────────────────────

const API_BASE = '/api'

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('auth_token')
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
}

async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = getAuthHeaders()
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { ...headers, ...(options.headers as Record<string, string> || {}) },
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `请求失败 (${res.status})`)
  }
  return res.json()
}

// ── Store ──────────────────────────────────────────────────

export const useInterviewStore = defineStore('interview', () => {
  const jobCategories = ref<JobCategory[]>([])
  const currentSession = ref<InterviewSession | null>(null)
  const currentQuestions = ref<QuestionItem[]>([])
  const aiMessages = ref<AIChatMessage[]>([])
  const report = ref<InterviewReport | null>(null)
  const historyItems = ref<InterviewHistoryItem[]>([])
  const loading = ref(false)

  const isActive = computed(() => currentSession.value?.status === 'in_progress')
  const currentRound = computed(() => currentSession.value?.current_round || '')

  async function fetchJobs() {
    loading.value = true
    try {
      jobCategories.value = await apiRequest<JobCategory[]>('/interview/jobs')
    } finally {
      loading.value = false
    }
  }

  async function startInterview(
    jobCategory: string,
    jobTitle: string,
    interviewMode: string = 'full',
    targetRound?: string | null,
  ): Promise<InterviewSession> {
    loading.value = true
    try {
      const session = await apiRequest<InterviewSession>('/interview/start', {
        method: 'POST',
        body: JSON.stringify({
          job_category: jobCategory,
          job_title: jobTitle,
          interview_mode: interviewMode,
          target_round: targetRound || null,
        }),
      })
      currentSession.value = session
      return session
    } finally {
      loading.value = false
    }
  }

  async function fetchSession(sessionId: string) {
    currentSession.value = await apiRequest<InterviewSession>(`/interview/session/${sessionId}`)
  }

  async function fetchQuestions(sessionId: string): Promise<QuestionItem[]> {
    const data = await apiRequest<{ round: string; questions: QuestionItem[] }>(
      `/interview/session/${sessionId}/question`
    )
    currentQuestions.value = data.questions
    return data.questions
  }

  async function submitAnswer(
    sessionId: string,
    questionId: string,
    answer: string | Record<string, unknown>,
    durationSeconds: number
  ): Promise<AnswerResponse> {
    return apiRequest<AnswerResponse>(`/interview/session/${sessionId}/answer`, {
      method: 'POST',
      body: JSON.stringify({
        question_id: questionId,
        answer,
        duration_seconds: durationSeconds,
      }),
    })
  }

  async function nextRound(sessionId: string): Promise<InterviewSession> {
    const session = await apiRequest<InterviewSession>(`/interview/session/${sessionId}/next`, {
      method: 'POST',
    })
    currentSession.value = session
    return session
  }

  async function sendAIChat(
    sessionId: string,
    messages: { role: string; content: string }[],
    round: string,
    onChunk: (text: string) => void,
    signal?: AbortSignal,
  ): Promise<string> {
    const token = localStorage.getItem('auth_token')
    const res = await fetch(`${API_BASE}/interview/session/${sessionId}/ai-chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ messages, round }),
      signal,
    })
    if (!res.ok) {
      throw new Error(`AI对话请求失败 (${res.status})`)
    }

    const reader = res.body?.getReader()
    const decoder = new TextDecoder()
    let fullText = ''

    if (reader) {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        const text = decoder.decode(value, { stream: true })
        const lines = text.split('\n')
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const dataStr = line.slice(6).trim()
          if (dataStr === '[DONE]') break
          try {
            const parsed = JSON.parse(dataStr)
            if (parsed.content) {
              fullText += parsed.content
              onChunk(fullText)
            }
          } catch { /* skip */ }
        }
      }
    }
    return fullText
  }

  async function reportCheat(sessionId: string, cheatCount: number) {
    const session = await apiRequest<InterviewSession>(`/interview/session/${sessionId}/cheat`, {
      method: 'POST',
      body: JSON.stringify({ cheat_count: cheatCount }),
    })
    currentSession.value = session
  }

  async function abortInterview(sessionId: string) {
    const session = await apiRequest<InterviewSession>(`/interview/session/${sessionId}/abort`, {
      method: 'POST',
    })
    currentSession.value = session
  }

  async function fetchReport(sessionId: string): Promise<InterviewReport> {
    report.value = await apiRequest<InterviewReport>(`/interview/session/${sessionId}/report`)
    return report.value
  }

  async function fetchHistory() {
    const data = await apiRequest<{ total: number; sessions: InterviewHistoryItem[] }>(
      '/interview/history'
    )
    historyItems.value = data.sessions
  }

  function resetSession() {
    currentSession.value = null
    currentQuestions.value = []
    aiMessages.value = []
    report.value = null
  }

  return {
    jobCategories,
    currentSession,
    currentQuestions,
    aiMessages,
    report,
    historyItems,
    loading,
    isActive,
    currentRound,
    fetchJobs,
    startInterview,
    fetchSession,
    fetchQuestions,
    submitAnswer,
    nextRound,
    sendAIChat,
    reportCheat,
    abortInterview,
    fetchReport,
    fetchHistory,
    resetSession,
  }
})
