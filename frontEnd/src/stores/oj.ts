import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'

// ── Types ─────────────────────────────────────────────────

export interface ProblemItem {
  id: string
  display_id: string
  title: string
  difficulty: string
  tags: string
  total_submissions: number
  accepted_submissions: number
  acceptance_rate: number
  user_solved: boolean
}

export interface ProblemDetail {
  id: string
  display_id: string
  title: string
  description: string
  input_format: string
  output_format: string
  constraints: string
  sample_input: string
  sample_output: string
  hint: string | null
  time_limit: number
  memory_limit: number
  difficulty: string
  tags: string
  total_submissions: number
  accepted_submissions: number
  acceptance_rate: number
  user_solved: boolean
  created_at: string
  updated_at: string
}

export interface SubmissionResult {
  id: string
  problem_id: string
  code: string
  language: string
  status: string
  execution_time: number | null
  execution_memory: number | null
  error_detail: string
  created_at: string
}

export interface DebugResult {
  stdout: string
  stderr: string
  exit_code: number
  execution_time: number
  status: string
}

export interface DifficultyProgress {
  difficulty: string
  total_problems: number
  solved: number
  attempted: number
}

export interface TagProgress {
  tag: string
  total: number
  solved: number
}

export interface UserProgress {
  total_submissions: number
  total_accepted: number
  total_problems_attempted: number
  total_problems_solved: number
  by_difficulty: DifficultyProgress[]
  by_tag: TagProgress[]
  recent_submissions: SubmissionResult[]
}

export interface ProblemFilters {
  difficulty: string | null
  tag: string | null
  keyword: string
}

// ── API Client ────────────────────────────────────────────

const API_BASE = '/api'

async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('auth_token')
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((options.headers as Record<string, string>) || {}),
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers })

  if (!res.ok) {
    if (res.status === 204) return undefined as T
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `请求失败 (${res.status})`)
  }

  return res.json()
}

// ── Store ─────────────────────────────────────────────────

const defaultFilters: ProblemFilters = {
  difficulty: null,
  tag: null,
  keyword: '',
}

export const useOjStore = defineStore('oj', () => {
  // State
  const problems = ref<ProblemItem[]>([])
  const currentProblem = ref<ProblemDetail | null>(null)
  const userProgress = ref<UserProgress | null>(null)
  const allTags = ref<string[]>([])
  const loading = ref(false)
  const total = ref(0)
  const page = ref(1)
  const size = ref(50)
  const filters = reactive<ProblemFilters>({ ...defaultFilters })

  // ── Actions ──────────────────────────────────────────

  function buildQueryString(): string {
    const params = new URLSearchParams()
    if (filters.difficulty) params.set('difficulty', filters.difficulty)
    if (filters.tag) params.set('tag', filters.tag)
    if (filters.keyword) params.set('keyword', filters.keyword)
    params.set('page', String(page.value))
    params.set('size', String(size.value))
    return params.toString()
  }

  async function fetchProblems() {
    loading.value = true
    try {
      const qs = buildQueryString()
      const data = await apiRequest<{
        problems: ProblemItem[]
        total: number
        page: number
        size: number
      }>(`/problems?${qs}`)
      problems.value = data.problems
      total.value = data.total
      page.value = data.page
      size.value = data.size
    } catch (e) {
      console.error('获取题目列表失败:', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchProblem(problemId: string) {
    loading.value = true
    try {
      currentProblem.value = await apiRequest<ProblemDetail>(
        `/problems/${problemId}`,
      )
    } catch (e) {
      console.error('获取题目详情失败:', e)
    } finally {
      loading.value = false
    }
  }

  async function submitCode(
    problemId: string,
    code: string,
    language: string,
  ): Promise<{ success: boolean; result?: SubmissionResult; message: string }> {
    try {
      const result = await apiRequest<SubmissionResult>(
        `/problems/${problemId}/submit`,
        {
          method: 'POST',
          body: JSON.stringify({ code, language }),
        },
      )
      return { success: true, result, message: '提交成功' }
    } catch (e: unknown) {
      return { success: false, message: (e as Error).message }
    }
  }

  async function debugCode(
    problemId: string,
    code: string,
    language: string,
    inputData: string,
  ): Promise<{ success: boolean; result?: DebugResult; message: string }> {
    try {
      const result = await apiRequest<DebugResult>(
        `/problems/${problemId}/debug`,
        {
          method: 'POST',
          body: JSON.stringify({ code, language, input_data: inputData }),
        },
      )
      return { success: true, result, message: '调试成功' }
    } catch (e: unknown) {
      return { success: false, message: (e as Error).message }
    }
  }

  async function fetchProgress() {
    try {
      userProgress.value = await apiRequest<UserProgress>('/problems/progress')
    } catch (e) {
      console.error('获取进度统计失败:', e)
    }
  }

  async function fetchAllTags() {
    try {
      const data = await apiRequest<{ tags: string[] }>('/problems/tags/options')
      allTags.value = data.tags
    } catch (e) {
      console.error('获取标签列表失败:', e)
    }
  }

  function resetFilters() {
    Object.assign(filters, defaultFilters)
    page.value = 1
  }

  function setPage(p: number) {
    page.value = p
  }

  return {
    // state
    problems,
    currentProblem,
    userProgress,
    allTags,
    loading,
    total,
    page,
    size,
    filters,
    // actions
    fetchProblems,
    fetchProblem,
    submitCode,
    debugCode,
    fetchProgress,
    fetchAllTags,
    resetFilters,
    setPage,
  }
})
