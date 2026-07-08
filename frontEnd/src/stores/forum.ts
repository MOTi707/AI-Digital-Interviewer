import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'

// ── Types ─────────────────────────────────────────────────

export interface TagItem {
  id: string
  name: string
}

export interface PostItem {
  id: string
  author_id: string
  title: string
  content: string
  company: string
  position: string
  year: number
  interview_type: string | null
  status: string
  is_anonymous: boolean
  likes_count: number
  comments_count: number
  created_at: string
  updated_at: string
  author_name: string
  tags: TagItem[]
  is_liked: boolean
}

export interface CommentItem {
  id: string
  post_id: string
  content: string
  is_anonymous: boolean
  created_at: string
  updated_at: string
  author_name: string
}

export interface TagStat {
  name: string
  count: number
}

export interface FilterOptions {
  companies: string[]
  positions: string[]
  statuses: string[]
  interview_types: string[]
  years: number[]
}

export interface PostFilters {
  company: string | null
  position: string | null
  year: number | null
  status: string | null
  interview_type: string | null
  tags: string[]
  keyword: string
  sort_by: 'latest' | 'hottest'
}

export interface PostCreateData {
  title: string
  content: string
  company: string
  position: string
  year: number
  interview_type: string | null
  status: string
  is_anonymous: boolean
  tag_names: string[]
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

const defaultFilters: PostFilters = {
  company: null,
  position: null,
  year: null,
  status: null,
  interview_type: null,
  tags: [],
  keyword: '',
  sort_by: 'latest',
}

export const useForumStore = defineStore('forum', () => {
  // State
  const posts = ref<PostItem[]>([])
  const currentPost = ref<PostItem | null>(null)
  const comments = ref<CommentItem[]>([])
  const tagStats = ref<TagStat[]>([])
  const filterOptions = ref<FilterOptions | null>(null)
  const loading = ref(false)
  const total = ref(0)
  const page = ref(1)
  const size = ref(20)
  const filters = reactive<PostFilters>({ ...defaultFilters })

  // ── Actions ──────────────────────────────────────────

  function buildQueryString(): string {
    const params = new URLSearchParams()
    if (filters.company) params.set('company', filters.company)
    if (filters.position) params.set('position', filters.position)
    if (filters.year) params.set('year', String(filters.year))
    if (filters.status) params.set('status', filters.status)
    if (filters.interview_type) params.set('interview_type', filters.interview_type)
    if (filters.tags.length) params.set('tags', filters.tags.join(','))
    if (filters.keyword) params.set('keyword', filters.keyword)
    if (filters.sort_by !== 'latest') params.set('sort_by', filters.sort_by)
    params.set('page', String(page.value))
    params.set('size', String(size.value))
    return params.toString()
  }

  async function fetchPosts() {
    loading.value = true
    try {
      const qs = buildQueryString()
      const data = await apiRequest<{ posts: PostItem[]; total: number; page: number; size: number }>(
        `/posts?${qs}`,
      )
      posts.value = data.posts
      total.value = data.total
      page.value = data.page
      size.value = data.size
    } catch (e) {
      console.error('获取帖子列表失败:', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchPost(postId: string) {
    loading.value = true
    try {
      currentPost.value = await apiRequest<PostItem>(`/posts/${postId}`)
    } catch (e) {
      console.error('获取帖子详情失败:', e)
    } finally {
      loading.value = false
    }
  }

  async function createPost(data: PostCreateData): Promise<{ success: boolean; message: string; post?: PostItem }> {
    try {
      const post = await apiRequest<PostItem>('/posts', {
        method: 'POST',
        body: JSON.stringify(data),
      })
      posts.value.unshift(post)
      total.value++
      return { success: true, message: '发布成功', post }
    } catch (e: unknown) {
      return { success: false, message: (e as Error).message }
    }
  }

  async function toggleLike(postId: string): Promise<boolean> {
    try {
      const result = await apiRequest<{ liked: boolean; message: string }>(`/posts/${postId}/like`, {
        method: 'POST',
      })
      // 更新本地状态
      const post = posts.value.find((p) => p.id === postId)
      if (post) {
        post.is_liked = result.liked
        post.likes_count += result.liked ? 1 : -1
      }
      if (currentPost.value?.id === postId) {
        currentPost.value.is_liked = result.liked
        currentPost.value.likes_count += result.liked ? 1 : -1
      }
      return result.liked
    } catch (e) {
      console.error('点赞操作失败:', e)
      return false
    }
  }

  async function fetchComments(postId: string) {
    try {
      const data = await apiRequest<{ comments: CommentItem[]; total: number }>(
        `/posts/${postId}/comments`,
      )
      comments.value = data.comments
    } catch (e) {
      console.error('获取评论失败:', e)
    }
  }

  async function createComment(
    postId: string,
    content: string,
    isAnonymous: boolean = false,
  ): Promise<{ success: boolean; message: string }> {
    try {
      const comment = await apiRequest<CommentItem>(`/posts/${postId}/comments`, {
        method: 'POST',
        body: JSON.stringify({ content, is_anonymous: isAnonymous }),
      })
      comments.value.push(comment)
      // 更新帖子评论数
      const post = posts.value.find((p) => p.id === postId)
      if (post) post.comments_count++
      if (currentPost.value?.id === postId) currentPost.value.comments_count++
      return { success: true, message: '评论成功' }
    } catch (e: unknown) {
      return { success: false, message: (e as Error).message }
    }
  }

  async function deletePost(postId: string): Promise<{ success: boolean; message: string }> {
    try {
      await apiRequest<void>(`/posts/${postId}`, { method: 'DELETE' })
      posts.value = posts.value.filter((p) => p.id !== postId)
      total.value--
      return { success: true, message: '已删除' }
    } catch (e: unknown) {
      return { success: false, message: (e as Error).message }
    }
  }

  async function deleteComment(commentId: string): Promise<{ success: boolean; message: string }> {
    try {
      await apiRequest<void>(`/posts/comments/${commentId}`, { method: 'DELETE' })
      comments.value = comments.value.filter((c) => c.id !== commentId)
      return { success: true, message: '评论已删除' }
    } catch (e: unknown) {
      return { success: false, message: (e as Error).message }
    }
  }

  async function fetchTagStats() {
    try {
      tagStats.value = await apiRequest<TagStat[]>('/posts/tags/stats')
    } catch (e) {
      console.error('获取标签统计失败:', e)
    }
  }

  async function fetchFilterOptions() {
    try {
      filterOptions.value = await apiRequest<FilterOptions>('/posts/filters/options')
    } catch (e) {
      console.error('获取筛选选项失败:', e)
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
    posts,
    currentPost,
    comments,
    tagStats,
    filterOptions,
    loading,
    total,
    page,
    size,
    filters,
    // actions
    fetchPosts,
    fetchPost,
    createPost,
    toggleLike,
    fetchComments,
    createComment,
    deletePost,
    deleteComment,
    fetchTagStats,
    fetchFilterOptions,
    resetFilters,
    setPage,
  }
})
