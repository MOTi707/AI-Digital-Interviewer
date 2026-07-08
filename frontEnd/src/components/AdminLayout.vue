<template>
  <div class="h-screen w-screen flex overflow-hidden bg-memphis-cream">
    <!-- 侧边栏 -->
    <aside class="shrink-0 w-64 bg-white border-r-4 border-black flex flex-col z-40 relative overflow-hidden">
      <!-- 装饰三角 -->
      <svg class="absolute -top-1 -right-1 w-16 h-16 opacity-10" viewBox="0 0 100 100">
        <polygon points="100,0 100,100 0,100" fill="#ff006e" />
      </svg>

      <!-- Logo -->
      <router-link
        to="/"
        class="block px-5 py-5 border-b-4 border-black font-black text-xl tracking-tight flex items-center gap-3 hover:bg-memphis-yellow transition-all duration-200 group"
      >
        <span class="inline-block w-9 h-9 bg-memphis-coral border-4 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] group-hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] group-hover:translate-x-[1px] group-hover:translate-y-[1px] transition-all" />
        <span>AI面试官</span>
      </router-link>

      <!-- 管理员标签 -->
      <div class="px-5 py-3 border-b-4 border-black bg-memphis-coral flex items-center gap-2">
        <span class="font-black text-[10px] px-2 py-1 bg-black text-white tracking-widest">ADMIN</span>
        <span class="font-black text-xs text-white tracking-tight">管理后台</span>
      </div>

      <!-- 导航菜单 -->
      <nav class="flex-1 overflow-y-auto py-3 space-y-1 px-3">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          :class="[
            'flex items-center gap-3 px-4 py-3 font-black text-sm border-4 border-black transition-all duration-200',
            isActive(item.path)
              ? 'bg-memphis-coral text-white shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]'
              : 'bg-white hover:bg-memphis-cream hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px]'
          ]"
        >
          <span class="text-lg">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </router-link>
      </nav>

      <!-- 底部操作区 -->
      <div class="border-t-4 border-black p-4 bg-memphis-cream space-y-2">
        <button
          @click="handleLogout"
          class="w-full flex items-center gap-3 border-4 border-black p-3 bg-memphis-coral text-white hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200"
        >
          <span class="text-lg">🚪</span>
          <span class="font-black text-sm">退出登录</span>
        </button>
      </div>
    </aside>

    <!-- 主内容 -->
    <main class="flex-1 overflow-y-auto bg-memphis-cream">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const menuItems = [
  { path: '/admin', label: '数据概览', icon: '📊' },
  { path: '/admin/users', label: '用户管理', icon: '👥' },
  { path: '/admin/problems', label: '题库管理', icon: '📝' },
  { path: '/admin/posts', label: '帖子管理', icon: '💬' },
]

function isActive(path: string) {
  if (path === '/admin') return route.path === '/admin'
  return route.path.startsWith(path)
}

const displayName = computed(() => authStore.user?.nickname || authStore.user?.username || '管理员')
const avatarText = computed(() => {
  const name = authStore.user?.nickname || authStore.user?.username || '管'
  return name.charAt(0).toUpperCase()
})

function clearAdminAuth() {
  localStorage.removeItem('admin_auth')
}

function handleLogout() {
  clearAdminAuth()
  router.push('/admin/login')
}
</script>
