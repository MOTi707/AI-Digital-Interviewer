<template>
  <div class="h-screen w-screen flex flex-col overflow-hidden bg-memphis-cream">
    <!-- 固定顶部导航栏 -->
    <nav class="shrink-0 bg-white border-b-4 border-black px-6 py-1.5 flex items-center justify-between z-50">
      <!-- 左侧 Logo + 模块导航 -->
      <div class="flex items-center gap-6">
        <router-link to="/" class="font-black text-lg tracking-tight flex items-center gap-2 shrink-0">
          <span class="inline-block w-7 h-7 bg-memphis-coral border-2 border-black" />
          <span>AI面试官</span>
        </router-link>

        <!-- 模块选择标签 -->
        <div class="flex gap-1">
          <button
            v-for="mod in modules"
            :key="mod.key"
            :class="[
              'px-4 py-1.5 font-black text-xs border-4 border-black transition-all duration-200',
              activeModule === mod.key
                ? `${mod.activeBg} text-white shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]`
                : 'bg-white text-black hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px]'
            ]"
            @click="handleModuleClick(mod)"
          >
            <span class="mr-1">{{ mod.icon }}</span>
            {{ mod.label }}
          </button>
        </div>
      </div>

      <!-- 右侧个人中心 -->
      <div class="shrink-0 relative">
        <button
          class="flex items-center gap-2 border-4 border-black bg-white px-4 py-1.5 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200"
          @click="showUserMenu = !showUserMenu"
        >
          <!-- 头像 -->
          <div class="w-7 h-7 border-2 border-black flex items-center justify-center font-black text-xs text-white overflow-hidden" :style="!authStore.user?.avatar ? { backgroundColor: authStore.user?.avatar_color || '#ff006e' } : {}">
            <img v-if="authStore.user?.avatar" :src="`/${authStore.user.avatar}`" class="w-full h-full object-cover" alt="" />
            <span v-else>{{ avatarText }}</span>
          </div>
          <!-- 用户名 -->
          <span class="font-black text-xs">{{ displayName }}</span>
          <!-- 下拉箭头 -->
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        <!-- 下拉菜单 -->
        <div
          v-if="showUserMenu"
          class="absolute right-0 top-full mt-2 w-48 bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] z-50"
        >
          <div class="px-4 py-3 border-b-4 border-black bg-memphis-cream">
            <div class="font-black text-sm">{{ displayName }}</div>
            <div class="font-mono text-xs text-gray-600 mt-0.5">{{ displayEmail }}</div>
          </div>
          <button
            class="w-full text-left px-4 py-2.5 font-bold text-sm hover:bg-memphis-yellow transition-colors border-b-2 border-black"
            @click="goToProfile"
          >
            👤 个人资料
          </button>
          <button
            class="w-full text-left px-4 py-2.5 font-bold text-sm hover:bg-memphis-yellow transition-colors border-b-2 border-black"
            @click="goToSettings"
          >
            ⚙️ 账号设置
          </button>
          <button
            v-if="isAdmin"
            class="w-full text-left px-4 py-2.5 font-bold text-sm hover:bg-memphis-purple hover:text-white transition-colors border-b-2 border-black"
            @click="goToAdmin"
          >
            🛡️ 管理后台
          </button>
          <button
            class="w-full text-left px-4 py-2.5 font-bold text-sm hover:bg-memphis-coral hover:text-white transition-colors"
            @click="handleLogout"
          >
            🚪 退出登录
          </button>
        </div>
      </div>
    </nav>

    <!-- 主内容区域 -->
    <main class="flex-1 overflow-hidden">
      <slot :active-module="activeModule" />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const showUserMenu = ref(false)

const modules = [
  { key: 'interview', label: '模拟面试', icon: '🎤', activeBg: 'bg-memphis-coral' },
  { key: 'career', label: '职业测评', icon: '🧭', activeBg: 'bg-memphis-yellow' },
  { key: 'resume', label: '简历分析', icon: '📄', activeBg: 'bg-memphis-purple', route: '/resume' },
  { key: 'forum', label: '面经论坛', icon: '💬', activeBg: 'bg-memphis-blue' },
  { key: 'oj', label: 'OJ刷题', icon: '🧩', activeBg: 'bg-[#22c55e]' },
]

const activeModule = ref(sessionStorage.getItem('dashboard_tab') || 'interview')

const displayName = computed(() => authStore.user?.nickname || authStore.user?.username || '用户')
const displayEmail = computed(() => authStore.user?.email || '未设置邮箱')
const avatarText = computed(() => {
  const name = authStore.user?.nickname || authStore.user?.username || '用'
  return name.charAt(0).toUpperCase()
})
const isAdmin = computed(() => {
  const email = authStore.user?.email || ''
  const username = authStore.user?.username || ''
  return email.includes('admin') || username.includes('admin')
})

function handleModuleClick(mod: { key: string; route?: string }) {
  if (mod.route) {
    router.push(mod.route)
  } else {
    activeModule.value = mod.key
    sessionStorage.setItem('dashboard_tab', mod.key)
  }
}

function handleLogout() {
  showUserMenu.value = false
  authStore.logout()
  router.push('/auth')
}

function goToSettings() {
  showUserMenu.value = false
  router.push('/settings')
}

function goToProfile() {
  showUserMenu.value = false
  router.push('/profile')
}
function goToAdmin() {
  showUserMenu.value = false
  router.push('/admin')
}
</script>
