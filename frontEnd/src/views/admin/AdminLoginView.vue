<template>
  <div class="min-h-screen w-screen bg-memphis-cream flex items-center justify-center relative overflow-hidden px-4">
    <!-- 背景装饰 -->
    <div class="absolute top-10 left-10 w-32 h-32 bg-memphis-coral opacity-20 rotate-12" />
    <div class="absolute bottom-20 right-16 w-24 h-24 bg-memphis-yellow opacity-20 -rotate-6" />
    <svg class="absolute top-1/4 right-1/4 w-20 h-20 opacity-10" viewBox="0 0 100 100">
      <polygon points="50,5 95,95 5,95" fill="#000" />
    </svg>
    <svg class="absolute bottom-1/3 left-1/5 w-16 h-16 opacity-10" viewBox="0 0 100 100">
      <circle cx="50" cy="50" r="45" fill="#ff006e" />
    </svg>
    <div class="absolute top-1/2 left-8 w-40 h-2 bg-memphis-teal opacity-20 rotate-45" />
    <div class="absolute bottom-1/4 right-1/3 w-28 h-2 bg-memphis-blue opacity-20 -rotate-12" />

    <!-- 登录卡片 -->
    <div class="relative z-10 w-full max-w-md">
      <!-- Logo -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center gap-3 mb-3">
          <div class="w-12 h-12 bg-memphis-coral border-4 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]" />
          <span class="font-black text-3xl md:text-4xl tracking-tight">AI面试官</span>
        </div>
        <p class="font-mono text-sm text-black/60 tracking-wide">ADMIN CONSOLE</p>
      </div>

      <!-- 卡片主体 -->
      <div class="bg-white border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] p-6 md:p-8">
        <div class="flex items-center gap-2 mb-6">
          <div class="w-2 h-8 bg-memphis-coral border-2 border-black" />
          <h2 class="font-black text-2xl tracking-tight">管理员登录</h2>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-5">
          <!-- 账号 -->
          <div>
            <label class="block font-black text-sm mb-2 tracking-wide">账号</label>
            <input
              v-model="account"
              type="text"
              placeholder="请输入管理员账号"
              class="w-full border-4 border-black px-4 py-3 font-sans text-sm focus:shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] focus:outline-none transition-all duration-200 bg-memphis-cream"
            />
          </div>

          <!-- 密码 -->
          <div>
            <label class="block font-black text-sm mb-2 tracking-wide">密码</label>
            <input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="请输入密码"
              class="w-full border-4 border-black px-4 py-3 font-sans text-sm focus:shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] focus:outline-none transition-all duration-200 bg-memphis-cream"
            />
            <button
              type="button"
              @click="showPassword = !showPassword"
              class="mt-1 font-mono text-xs text-black/50 hover:text-black transition-colors"
            >
              {{ showPassword ? '🔒 隐藏密码' : '👁 显示密码' }}
            </button>
          </div>

          <!-- 错误提示 -->
          <div
            v-if="errorMsg"
            class="border-4 border-black bg-memphis-coral text-white p-3 font-black text-sm flex items-center gap-2 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]"
          >
            <span>⚠️</span>
            <span>{{ errorMsg }}</span>
          </div>

          <!-- 登录按钮 -->
          <button
            type="submit"
            class="w-full bg-black text-white font-black text-base py-3 md:py-4 border-4 border-black shadow-[5px_5px_0px_0px_rgba(255,0,110,1)] hover:shadow-[2px_2px_0px_0px_rgba(255,0,110,1)] hover:translate-x-[3px] hover:translate-y-[3px] active:shadow-none active:translate-x-[5px] active:translate-y-[5px] transition-all duration-200 tracking-wider"
          >
            确认登录
          </button>
        </form>
      </div>

      <!-- 底部装饰 -->
      <div class="flex items-center justify-center gap-2 mt-6">
        <div class="w-8 h-1 bg-memphis-coral" />
        <div class="w-8 h-1 bg-memphis-yellow" />
        <div class="w-8 h-1 bg-memphis-teal" />
        <div class="w-8 h-1 bg-memphis-blue" />
      </div>
      <p class="text-center font-mono text-xs text-black/40 mt-3">Management System v1.0</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const account = ref('')
const password = ref('')
const showPassword = ref(false)
const errorMsg = ref('')

async function handleLogin() {
  errorMsg.value = ''

  if (!account.value || !password.value) {
    errorMsg.value = '请输入账号和密码'
    return
  }

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ account: account.value, password: password.value }),
    })
    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      throw new Error(body.detail || '登录失败')
    }
    const data = await res.json()
    localStorage.setItem('auth_token', data.access_token)
    localStorage.setItem('admin_auth', 'true')
    router.push('/admin')
  } catch (e: unknown) {
    errorMsg.value = e instanceof Error ? e.message : '登录失败，请检查账号密码'
  }
}
</script>
