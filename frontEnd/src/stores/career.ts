import { defineStore } from 'pinia'
import { ref } from 'vue'

const API_BASE = '/api'

function authHeaders(): Record<string, string> {
  const token = localStorage.getItem('auth_token')
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  return headers
}

async function apiReq<T>(path: string, opts: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { ...opts, headers: authHeaders() })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `请求失败 (${res.status})`)
  }
  return res.json()
}

// ── 类型定义 ─────────────────────────────────────────────

export interface QuestionOption {
  label: string
  value: number
}

export interface QuestionItem {
  id: string
  dimension: string
  text: string
  options: QuestionOption[]
}

export interface QuestionsData {
  type: string
  title: string
  description: string
  questions: QuestionItem[]
}

export interface AnswerEntry {
  question_id: string
  score: number
}

export interface AssessmentRecord {
  id: string
  type: string
  result: Record<string, unknown>
  summary: string | null
  created_at: string
}

export interface AssessmentList {
  total: number
  items: AssessmentRecord[]
}

export interface RecommendedJob {
  title: string
  match: number
  reason: string
  salary_range: string
}

export interface PrepTip {
  category: string
  tips: string[]
}

export interface CareerRecommendation {
  jobs: RecommendedJob[]
  prep_tips: PrepTip[]
  loading: boolean
  error: string | null
}

// ── Store ────────────────────────────────────────────────

export const useCareerStore = defineStore('career', () => {
  const currentQuestions = ref<QuestionsData | null>(null)
  const history = ref<AssessmentList>({ total: 0, items: [] })
  const loading = ref(false)
  const error = ref<string | null>(null)
  const recommendation = ref<CareerRecommendation>({
    jobs: [],
    prep_tips: [],
    loading: false,
    error: null,
  })

  async function fetchQuestions(type: string) {
    loading.value = true
    error.value = null
    try {
      currentQuestions.value = await apiReq<QuestionsData>(`/career/questions/${type}`)
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  async function submitAssessment(type: string, answers: AnswerEntry[]): Promise<AssessmentRecord | null> {
    loading.value = true
    error.value = null
    try {
      const record = await apiReq<AssessmentRecord>('/career/submit', {
        method: 'POST',
        body: JSON.stringify({ type, answers }),
      })
      return record
    } catch (e) {
      error.value = (e as Error).message
      return null
    } finally {
      loading.value = false
    }
  }

  async function fetchHistory() {
    loading.value = true
    error.value = null
    try {
      history.value = await apiReq<AssessmentList>('/career/history')
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  async function fetchResult(id: string): Promise<AssessmentRecord | null> {
    loading.value = true
    error.value = null
    try {
      return await apiReq<AssessmentRecord>(`/career/result/${id}`)
    } catch (e) {
      error.value = (e as Error).message
      return null
    } finally {
      loading.value = false
    }
  }

  async function fetchRecommendation(assessmentId: string) {
    recommendation.value = {
      jobs: [],
      prep_tips: [],
      loading: true,
      error: null,
    }

    const token = localStorage.getItem('auth_token')
    const headers: Record<string, string> = { 'Content-Type': 'application/json' }
    if (token) headers['Authorization'] = `Bearer ${token}`

    try {
      const res = await fetch(`${API_BASE}/career/recommend/stream`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ assessment_id: assessmentId }),
      })

      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error(body.detail || `请求失败 (${res.status})`)
      }

      const reader = res.body?.getReader()
      if (!reader) throw new Error('无法读取响应流')

      const decoder = new TextDecoder()
      let buf = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buf += decoder.decode(value, { stream: true })

        // 解析 SSE data: 行
        const lines = buf.split('\n')
        buf = lines.pop() || ''
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const payload = line.slice(6).trim()
          if (!payload) continue
          try {
            const msg = JSON.parse(payload)
            if (msg.type === 'job') {
              recommendation.value.jobs.push(msg.data)
            } else if (msg.type === 'done') {
              recommendation.value.prep_tips = msg.prep_tips || []
            }
          } catch {
            // ignore malformed chunks
          }
        }
      }
    } catch (e) {
      recommendation.value.error = (e as Error).message
    } finally {
      recommendation.value.loading = false
    }
  }

  return {
    currentQuestions,
    history,
    loading,
    error,
    recommendation,
    fetchQuestions,
    submitAssessment,
    fetchHistory,
    fetchResult,
    fetchRecommendation,
  }
})

