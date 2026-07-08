<template>
  <div class="h-screen w-screen flex flex-col overflow-hidden bg-memphis-cream">
    <!-- 顶部导航栏 -->
    <nav class="shrink-0 bg-white border-b-4 border-black px-6 py-1.5 flex items-center justify-between z-50">
      <div class="flex items-center gap-4">
        <router-link
          to="/dashboard"
          class="flex items-center gap-2 px-3 py-1.5 border-4 border-black bg-white font-black text-sm hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200"
        >
          ← 返回仪表盘
        </router-link>
        <div class="flex items-center gap-2">
          <div class="w-7 h-7 bg-memphis-coral border-2 border-black flex items-center justify-center">
            <span class="text-sm">⚙️</span>
          </div>
          <span class="font-black text-xl tracking-tight">账号设置</span>
        </div>
      </div>
    </nav>

    <!-- 主内容 -->
    <main class="flex-1 overflow-y-auto px-4 md:px-8 py-8">
      <div class="max-w-2xl mx-auto space-y-6">
        <!-- 账号信息卡片 -->
        <section class="border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] bg-white p-6">
          <h2 class="font-black text-xl tracking-tight mb-4">👤 账号信息</h2>
          <div class="space-y-3">
            <div class="flex items-center gap-3">
              <span class="font-black text-sm w-20 shrink-0">用户名</span>
              <span class="font-mono text-sm bg-memphis-cream px-3 py-1.5 border-2 border-black flex-1">
                {{ authStore.user?.username || '-' }}
              </span>
            </div>
            <div class="flex items-center gap-3">
              <span class="font-black text-sm w-20 shrink-0">邮箱</span>
              <span class="font-mono text-sm bg-memphis-cream px-3 py-1.5 border-2 border-black flex-1">
                {{ authStore.user?.email || '未设置' }}
              </span>
            </div>
            <div class="flex items-center gap-3">
              <span class="font-black text-sm w-20 shrink-0">注册时间</span>
              <span class="font-mono text-sm bg-memphis-cream px-3 py-1.5 border-2 border-black flex-1">
                {{ formatDate(authStore.user?.created_at) }}
              </span>
            </div>
          </div>
        </section>

        <!-- 修改用户名 -->
        <section class="border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] bg-white p-6">
          <h2 class="font-black text-xl tracking-tight mb-4">✏️ 修改用户名</h2>
          <div class="flex gap-3">
            <input
              v-model="newUsername"
              type="text"
              placeholder="新用户名（3-50字符）"
              class="flex-1 border-4 border-black font-sans focus:shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] focus:outline-none px-3 py-2 text-sm"
            />
            <button
              class="px-5 py-2 border-4 border-black bg-memphis-coral text-white font-black text-sm shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200 disabled:opacity-40"
              :disabled="usernameLoading || !newUsername.trim()"
              @click="handleUpdateUsername"
            >
              {{ usernameLoading ? '...' : '修改' }}
            </button>
          </div>
          <p v-if="usernameMsg" :class="['font-mono text-xs mt-2', usernameOk ? 'text-green-600' : 'text-red-500']">
            {{ usernameMsg }}
          </p>
        </section>

        <!-- 修改邮箱 -->
        <section class="border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] bg-white p-6">
          <h2 class="font-black text-xl tracking-tight mb-4">📧 修改邮箱</h2>
          <div class="flex gap-3">
            <input
              v-model="newEmail"
              type="email"
              placeholder="新邮箱地址"
              class="flex-1 border-4 border-black font-sans focus:shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] focus:outline-none px-3 py-2 text-sm"
            />
            <button
              class="px-5 py-2 border-4 border-black bg-memphis-blue text-white font-black text-sm shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200 disabled:opacity-40"
              :disabled="emailLoading || !newEmail.trim()"
              @click="handleUpdateEmail"
            >
              {{ emailLoading ? '...' : '修改' }}
            </button>
          </div>
          <p v-if="emailMsg" :class="['font-mono text-xs mt-2', emailOk ? 'text-green-600' : 'text-red-500']">
            {{ emailMsg }}
          </p>
        </section>

        <!-- 修改密码 -->
        <section class="border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] bg-white p-6">
          <h2 class="font-black text-xl tracking-tight mb-4">🔒 修改密码</h2>
          <div class="space-y-3">
            <input
              v-model="oldPassword"
              type="password"
              placeholder="当前密码"
              class="w-full border-4 border-black font-sans focus:shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] focus:outline-none px-3 py-2 text-sm"
            />
            <input
              v-model="newPassword"
              type="password"
              placeholder="新密码（至少6位）"
              class="w-full border-4 border-black font-sans focus:shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] focus:outline-none px-3 py-2 text-sm"
            />
            <input
              v-model="confirmPassword"
              type="password"
              placeholder="确认新密码"
              class="w-full border-4 border-black font-sans focus:shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] focus:outline-none px-3 py-2 text-sm"
            />
            <button
              class="w-full py-2 border-4 border-black bg-memphis-yellow font-black text-sm shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200 disabled:opacity-40"
              :disabled="passwordLoading || !oldPassword || !newPassword || !confirmPassword"
              @click="handleChangePassword"
            >
              {{ passwordLoading ? '...' : '修改密码' }}
            </button>
          </div>
          <p v-if="passwordMsg" :class="['font-mono text-xs mt-2', passwordOk ? 'text-green-600' : 'text-red-500']">
            {{ passwordMsg }}
          </p>
        </section>

        <!-- 注销账号 -->
        <section class="border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] bg-red-50 p-6">
          <h2 class="font-black text-xl tracking-tight mb-2 text-red-600">⚠️ 注销账号</h2>
          <p class="font-mono text-xs text-red-500 mb-4">
            注销后账号将被停用，所有数据保留但无法登录。此操作不可撤销。
          </p>
          <div class="flex gap-3">
            <input
              v-model="deletePassword"
              type="password"
              placeholder="输入密码确认注销"
              class="flex-1 border-4 border-black font-sans focus:shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] focus:outline-none px-3 py-2 text-sm"
            />
            <button
              class="px-5 py-2 border-4 border-black bg-black text-white font-black text-sm shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200 disabled:opacity-40"
              :disabled="deleteLoading || !deletePassword"
              @click="handleDeleteAccount"
            >
              {{ deleteLoading ? '...' : '注销' }}
            </button>
          </div>
          <p v-if="deleteMsg" :class="['font-mono text-xs mt-2', deleteOk ? 'text-green-600' : 'text-red-500']">
            {{ deleteMsg }}
          </p>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 修改用户名
const newUsername = ref('')
const usernameLoading = ref(false)
const usernameMsg = ref('')
const usernameOk = ref(false)

// 修改邮箱
const newEmail = ref('')
const emailLoading = ref(false)
const emailMsg = ref('')
const emailOk = ref(false)

// 修改密码
const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const passwordLoading = ref(false)
const passwordMsg = ref('')
const passwordOk = ref(false)

// 注销账号
const deletePassword = ref('')
const deleteLoading = ref(false)
const deleteMsg = ref('')
const deleteOk = ref(false)

function formatDate(dt?: string | null): string {
  if (!dt) return '未知'
  try {
    return new Date(dt).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  } catch {
    return dt
  }
}

async function handleUpdateUsername() {
  usernameLoading.value = true
  usernameMsg.value = ''
  const res = await authStore.updateUsername(newUsername.value.trim())
  usernameOk.value = res.success
  usernameMsg.value = res.message
  if (res.success) newUsername.value = ''
  usernameLoading.value = false
}

async function handleUpdateEmail() {
  emailLoading.value = true
  emailMsg.value = ''
  const res = await authStore.updateEmail(newEmail.value.trim())
  emailOk.value = res.success
  emailMsg.value = res.message
  if (res.success) newEmail.value = ''
  emailLoading.value = false
}

async function handleChangePassword() {
  if (newPassword.value !== confirmPassword.value) {
    passwordMsg.value = '两次输入的密码不一致'
    passwordOk.value = false
    return
  }
  passwordLoading.value = true
  passwordMsg.value = ''
  const res = await authStore.changePassword(oldPassword.value, newPassword.value)
  passwordOk.value = res.success
  passwordMsg.value = res.message
  if (res.success) {
    oldPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
  }
  passwordLoading.value = false
}

async function handleDeleteAccount() {
  if (!confirm('确定要注销账号吗？此操作不可撤销。')) return
  deleteLoading.value = true
  deleteMsg.value = ''
  const res = await authStore.deleteAccount(deletePassword.value)
  deleteOk.value = res.success
  deleteMsg.value = res.message
  if (res.success) {
    router.push('/auth')
  }
  deleteLoading.value = false
}

onMounted(() => {
  authStore.fetchProfile().catch(() => {})
})
</script>
