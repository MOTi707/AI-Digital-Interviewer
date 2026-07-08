import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'

// ── Types ──────────────────────────────────────────────

export interface DashboardStats {
  total_users: number
  total_problems: number
  total_posts: number
  total_interviews: number
  active_users_today: number
  new_users_this_week: number
}

export interface AdminUser {
  id: string
  username: string
  email: string | null
  nickname: string | null
  is_active: boolean
  created_at: string
}

export interface AdminProblem {
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
  created_at: string
}

export interface AdminPost {
  id: string
  title: string
  author_id: string
  author_name: string
  company: string
  position: string
  likes_count: number
  comments_count: number
  status: string
  created_at: string
}

// ── API helpers ────────────────────────────────────────

const API_BASE = '/api'

async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('auth_token')
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `请求失败 (${res.status})`)
  }
  return res.json()
}

// ── Store ──────────────────────────────────────────────

export const useAdminStore = defineStore('admin', () => {
  // Dashboard
  const stats = ref<DashboardStats | null>(null)
  const statsLoading = ref(false)

  // Users
  const users = ref<AdminUser[]>([])
  const usersTotal = ref(0)
  const usersLoading = ref(false)
  const userFilters = reactive({ keyword: '', page: 1, size: 15 })

  // Problems
  const problems = ref<AdminProblem[]>([])
  const problemsTotal = ref(0)
  const problemsLoading = ref(false)
  const problemFilters = reactive({ keyword: '', difficulty: '', page: 1, size: 15 })

  // Posts
  const posts = ref<AdminPost[]>([])
  const postsTotal = ref(0)
  const postsLoading = ref(false)
  const postFilters = reactive({ keyword: '', page: 1, size: 15 })

  // ── Dashboard ──────────────────────────────────────

  async function fetchStats() {
    statsLoading.value = true
    try {
      stats.value = await apiRequest<DashboardStats>('/admin/stats')
    } catch (e) {
      console.error('获取统计数据失败:', e)
    } finally {
      statsLoading.value = false
    }
  }

  // ── Users ──────────────────────────────────────────

  async function fetchUsers() {
    usersLoading.value = true
    try {
      const params = new URLSearchParams()
      if (userFilters.keyword) params.set('keyword', userFilters.keyword)
      params.set('page', String(userFilters.page))
      params.set('size', String(userFilters.size))
      const data = await apiRequest<{
        users: AdminUser[]
        total: number
        page: number
        size: number
      }>(`/admin/users?${params}`)
      users.value = data.users
      usersTotal.value = data.total
    } catch (e) {
      console.error('获取用户列表失败:', e)
    } finally {
      usersLoading.value = false
    }
  }

  async function toggleUserStatus(userId: string, isActive: boolean) {
    await apiRequest(`/admin/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify({ is_active: isActive }),
    })
    const u = users.value.find(u => u.id === userId)
    if (u) u.is_active = isActive
  }

  async function deleteUser(userId: string) {
    await apiRequest(`/admin/users/${userId}`, { method: 'DELETE' })
    users.value = users.value.filter(u => u.id !== userId)
    usersTotal.value--
  }

  // ── Problems ───────────────────────────────────────

  async function fetchProblems() {
    problemsLoading.value = true
    try {
      const params = new URLSearchParams()
      if (problemFilters.keyword) params.set('keyword', problemFilters.keyword)
      if (problemFilters.difficulty) params.set('difficulty', problemFilters.difficulty)
      params.set('page', String(problemFilters.page))
      params.set('size', String(problemFilters.size))
      const data = await apiRequest<{
        problems: AdminProblem[]
        total: number
        page: number
        size: number
      }>(`/admin/problems?${params}`)
      problems.value = data.problems
      problemsTotal.value = data.total
    } catch (e) {
      console.error('获取题目列表失败:', e)
    } finally {
      problemsLoading.value = false
    }
  }

  async function createProblem(data: Record<string, unknown>) {
    const created = await apiRequest<AdminProblem>('/admin/problems', {
      method: 'POST',
      body: JSON.stringify(data),
    })
    return created
  }

  async function updateProblem(problemId: string, data: Record<string, unknown>) {
    const updated = await apiRequest<AdminProblem>(`/admin/problems/${problemId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
    const idx = problems.value.findIndex(p => p.id === problemId)
    if (idx !== -1) problems.value[idx] = updated
    return updated
  }

  async function deleteProblem(problemId: string) {
    await apiRequest(`/admin/problems/${problemId}`, { method: 'DELETE' })
    problems.value = problems.value.filter(p => p.id !== problemId)
    problemsTotal.value--
  }

  // ── Posts ──────────────────────────────────────────

  async function fetchPosts() {
    postsLoading.value = true
    try {
      const params = new URLSearchParams()
      if (postFilters.keyword) params.set('keyword', postFilters.keyword)
      params.set('page', String(postFilters.page))
      params.set('size', String(postFilters.size))
      const data = await apiRequest<{
        posts: AdminPost[]
        total: number
        page: number
        size: number
      }>(`/admin/posts?${params}`)
      posts.value = data.posts
      postsTotal.value = data.total
    } catch (e) {
      console.error('获取帖子列表失败:', e)
    } finally {
      postsLoading.value = false
    }
  }

  async function deletePost(postId: string) {
    await apiRequest(`/admin/posts/${postId}`, { method: 'DELETE' })
    posts.value = posts.value.filter(p => p.id !== postId)
    postsTotal.value--
  }

  return {
    stats,
    statsLoading,
    users,
    usersTotal,
    usersLoading,
    userFilters,
    problems,
    problemsTotal,
    problemsLoading,
    problemFilters,
    posts,
    postsTotal,
    postsLoading,
    postFilters,
    fetchStats,
    fetchUsers,
    toggleUserStatus,
    deleteUser,
    fetchProblems,
    createProblem,
    updateProblem,
    deleteProblem,
    fetchPosts,
    deletePost,
  }
})
