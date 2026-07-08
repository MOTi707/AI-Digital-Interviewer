import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// ── Types ────────────────────────────────────────────────

export interface ResumeData {
  id: string
  file_name: string
  raw_text: string
  file_path: string | null
  parsed_content: ParsedContent | null
  skill_keywords: string[] | null
  created_at: string
  updated_at: string
}

export interface ParsedContent {
  skills: string[]
  experiences: Experience[]
  education: Education[]
  summary?: string
  score?: number
  suggestions?: Suggestion[]
  skill_categories?: SkillCategory[]
}

export interface Experience {
  role: string
  company: string
  period: string
  duration: string
  description?: string
}

export interface Education {
  school: string
  degree: string
  period: string
}

export interface Suggestion {
  title: string
  desc: string
  type: 'warning' | 'success' | 'info'
}

export interface SkillCategory {
  name: string
  keywords: string[]
  percent: number
}

export interface OptimizeResult {
  original: { text: string; type: string }[]
  optimized: { text: string; type: string }[]
  stats: Record<string, unknown>
}

// ── API helpers ──────────────────────────────────────────

const API_BASE = '/api'

async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('auth_token')
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `请求失败 (${res.status})`)
  }
  return res.json()
}

// ── Store ────────────────────────────────────────────────

export const useResumeStore = defineStore('resume', () => {
  const resume = ref<ResumeData | null>(null)
  const loading = ref(false)
  const analyzing = ref(false)
  const optimizing = ref(false)
  const hasApiKey = ref(false)

  const hasResume = computed(() => !!resume.value)
  const hasParsedContent = computed(() => !!resume.value?.parsed_content)

  /** 获取后端配置（是否有 API Key） */
  async function fetchConfig() {
    try {
      const config = await apiRequest<{ has_api_key: boolean }>('/resume/config')
      hasApiKey.value = config.has_api_key
    } catch {
      hasApiKey.value = false
    }
  }

  /** 获取当前用户简历 */
  async function fetchResume() {
    loading.value = true
    try {
      resume.value = await apiRequest<ResumeData>('/resume/')
    } catch {
      resume.value = null
    } finally {
      loading.value = false
    }
  }

  /** 上传/覆盖简历 */
  async function uploadResume(file: File, rawText: string) {
    loading.value = true
    try {
      const token = localStorage.getItem('auth_token')
      const formData = new FormData()
      formData.append('file', file)
      formData.append('raw_text', rawText)
      const res = await fetch('/api/resume/upload', {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: formData,
      })
      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error(body.detail || `请求失败 (${res.status})`)
      }
      resume.value = await res.json()
    } finally {
      loading.value = false
    }
  }

  /** 手动触发 AI 分析 */
  async function analyzeResume() {
    analyzing.value = true
    try {
      resume.value = await apiRequest<ResumeData>('/resume/analyze', {
        method: 'POST',
      })
    } finally {
      analyzing.value = false
    }
  }

  /** AI 措辞优化 */
  async function optimizeText(): Promise<OptimizeResult> {
    optimizing.value = true
    try {
      return await apiRequest<OptimizeResult>('/resume/optimize', {
        method: 'POST',
      })
    } finally {
      optimizing.value = false
    }
  }

  /** 流式 AI 措辞优化 - 边生成边回调 */
  async function optimizeTextStream(
    onItem: (idx: number, original: string, optimized: string) => void,
    onDone: (stats: Record<string, unknown>) => void,
    onStart?: () => void,
    silent = false,
  ): Promise<void> {
    if (!silent) optimizing.value = true
    try {
      const token = localStorage.getItem('auth_token')
      const res = await fetch('/api/resume/optimize/stream', {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      })
      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error(body.detail || `请求失败 (${res.status})`)
      }
      const reader = res.body!.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        // 按 SSE 格式拆分
        const parts = buffer.split('\n\n')
        buffer = parts.pop() || ''
        for (const part of parts) {
          for (const line of part.split('\n')) {
            if (!line.startsWith('data: ')) continue
            try {
              const msg = JSON.parse(line.slice(6))
              if (msg.type === 'start') {
                onStart?.()
              } else if (msg.type === 'item') {
                onItem(msg.index, msg.data.original, msg.data.optimized)
              } else if (msg.type === 'done') {
                onDone(msg.stats)
              }
            } catch { /* ignore parse errors */ }
          }
        }
      }
    } finally {
      if (!silent) optimizing.value = false
    }
  }

  /** 服务端提取 PDF 文本 */
  async function extractPdfText(file: File): Promise<string> {
    const token = localStorage.getItem('auth_token')
    const formData = new FormData()
    formData.append('file', file)
    const res = await fetch('/api/resume/extract-text', {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    })
    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      throw new Error(body.detail || `PDF 提取失败 (${res.status})`)
    }
    const data = await res.json()
    return data.raw_text
  }

  return {
    resume,
    loading,
    analyzing,
    optimizing,
    hasApiKey,
    hasResume,
    hasParsedContent,
    fetchConfig,
    fetchResume,
    uploadResume,
    analyzeResume,
    optimizeText,
    optimizeTextStream,
    extractPdfText,
  }
})
