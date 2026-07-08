import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface User {
  id: string
  username: string
  email: string | null
  nickname: string | null
  avatar: string | null
  avatar_color: string | null
  bio: string | null
  phone: string | null
  gender: string | null
  birth_date: string | null
  created_at?: string | null
}

export interface ProfileUpdate {
  nickname?: string | null
  avatar_color?: string | null
  bio?: string | null
  phone?: string | null
  gender?: string | null
  birth_date?: string | null
}

interface TokenResponse {
  access_token: string
  token_type: string
  user: User
}

// ── API Client ────────────────────────────────────────────

const API_BASE = '/api'

async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = localStorage.getItem('auth_token')
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  })

  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `请求失败 (${res.status})`)
  }

  return res.json()
}

// ── Store ─────────────────────────────────────────────────

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  /** 应用启动时调用：恢复本地 token 并验证有效性 */
  async function init() {
    const savedToken = localStorage.getItem('auth_token')
    if (!savedToken) return

    token.value = savedToken
    try {
      user.value = await apiRequest<User>('/auth/me')
    } catch {
      // Token 无效，清除
      logout()
    }
  }

  /** 邮箱注册 */
  async function registerByEmail(
    email: string,
    password: string,
  ): Promise<{ success: boolean; message: string }> {
    try {
      const data = await apiRequest<TokenResponse>('/auth/register/email', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })
      _setSession(data)
      return { success: true, message: '注册成功' }
    } catch (e: unknown) {
      return { success: false, message: (e as Error).message }
    }
  }

  /** 用户名注册 */
  async function registerByUsername(
    username: string,
    password: string,
  ): Promise<{ success: boolean; message: string }> {
    try {
      const data = await apiRequest<TokenResponse>('/auth/register/username', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      })
      _setSession(data)
      return { success: true, message: '注册成功' }
    } catch (e: unknown) {
      return { success: false, message: (e as Error).message }
    }
  }

  /** 登录（邮箱/用户名） */
  async function login(
    account: string,
    password: string,
  ): Promise<{ success: boolean; message: string }> {
    try {
      const data = await apiRequest<TokenResponse>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ account, password }),
      })
      _setSession(data)
      return { success: true, message: '登录成功' }
    } catch (e: unknown) {
      return { success: false, message: (e as Error).message }
    }
  }

  /** 登出 */
  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_user')
  }

  /** 获取完整个人资料 */
  async function fetchProfile(): Promise<User | null> {
    try {
      const data = await apiRequest<User>('/auth/profile')
      user.value = data
      localStorage.setItem('auth_user', JSON.stringify(data))
      return data
    } catch {
      return null
    }
  }

  /** 更新个人资料 */
  async function updateProfile(
    profileData: ProfileUpdate,
  ): Promise<{ success: boolean; message: string }> {
    try {
      const data = await apiRequest<User>('/auth/profile', {
        method: 'PUT',
        body: JSON.stringify(profileData),
      })
      user.value = data
      localStorage.setItem('auth_user', JSON.stringify(data))
      return { success: true, message: '资料更新成功' }
    } catch (e: unknown) {
      return { success: false, message: (e as Error).message }
    }
  }

  /** 修改密码 */
  async function changePassword(
    oldPassword: string,
    newPassword: string,
  ): Promise<{ success: boolean; message: string }> {
    try {
      await apiRequest<{ message: string }>('/auth/password', {
        method: 'PUT',
        body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
      })
      return { success: true, message: '密码修改成功' }
    } catch (e: unknown) {
      return { success: false, message: (e as Error).message }
    }
  }

  /** 上传头像 */
  async function uploadAvatar(
    file: File,
  ): Promise<{ success: boolean; message: string }> {
    try {
      const token = localStorage.getItem('auth_token')
      const formData = new FormData()
      formData.append('file', file)

      const res = await fetch(`${API_BASE}/auth/avatar`, {
        method: 'POST',
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: formData,
      })

      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error(body.detail || `请求失败 (${res.status})`)
      }

      const data = await res.json() as User
      user.value = data
      localStorage.setItem('auth_user', JSON.stringify(data))
      return { success: true, message: '头像更新成功' }
    } catch (e: unknown) {
      return { success: false, message: (e as Error).message }
    }
  }

  // ── Account Settings Methods ───────────────────────

  /** 修改用户名 */
  async function updateUsername(
    username: string,
  ): Promise<{ success: boolean; message: string }> {
    try {
      const data = await apiRequest<TokenResponse>('/auth/username', {
        method: 'PUT',
        body: JSON.stringify({ username }),
      })
      _setSession(data)
      return { success: true, message: '用户名修改成功' }
    } catch (e: unknown) {
      return { success: false, message: (e as Error).message }
    }
  }

  /** 修改邮箱 */
  async function updateEmail(
    email: string,
  ): Promise<{ success: boolean; message: string }> {
    try {
      const data = await apiRequest<TokenResponse>('/auth/email', {
        method: 'PUT',
        body: JSON.stringify({ email }),
      })
      _setSession(data)
      return { success: true, message: '邮箱修改成功' }
    } catch (e: unknown) {
      return { success: false, message: (e as Error).message }
    }
  }

  /** 修改密码 */
  async function changePasswordBySettings(
    oldPassword: string,
    newPassword: string,
  ): Promise<{ success: boolean; message: string }> {
    try {
      const data = await apiRequest<{ message: string }>('/auth/password', {
        method: 'PUT',
        body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
      })
      return { success: true, message: data.message }
    } catch (e: unknown) {
      return { success: false, message: (e as Error).message }
    }
  }

  /** 注销账号 */
  async function deleteAccount(
    password: string,
  ): Promise<{ success: boolean; message: string }> {
    try {
      await apiRequest<{ message: string }>('/auth/account', {
        method: 'DELETE',
        body: JSON.stringify({ password }),
      })
      logout()
      return { success: true, message: '账号已注销' }
    } catch (e: unknown) {
      return { success: false, message: (e as Error).message }
    }
  }

  // ── 内部方法 ──────────────────────────────────────────

  function _setSession(data: TokenResponse) {
    token.value = data.access_token
    user.value = data.user
    localStorage.setItem('auth_token', data.access_token)
    localStorage.setItem('auth_user', JSON.stringify(data.user))
  }

  return {
    user,
    token,
    isAuthenticated,
    init,
    registerByEmail,
    registerByUsername,
    login,
    logout,
    fetchProfile,
    updateProfile,
    changePassword,
    uploadAvatar,
    updateUsername,
    updateEmail,
    changePasswordBySettings,
    deleteAccount,
  }
})
