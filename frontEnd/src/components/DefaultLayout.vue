<template>
  <div class="min-h-screen flex flex-col">
    <!-- 导航栏 -->
    <nav class="bg-white border-b-2 md:border-b-4 border-black px-4 md:px-8 py-3 md:py-4 sticky top-0 z-50">
      <div class="flex items-center justify-between max-w-screen-2xl mx-auto">
        <router-link to="/" class="font-black text-xl md:text-2xl tracking-tight flex items-center gap-2">
          <span class="inline-block w-8 h-8 md:w-10 md:h-10 bg-memphis-coral border-2 border-black" />
          <span>AI面试官</span>
        </router-link>
        <div class="hidden md:flex gap-6 md:gap-8 font-mono text-sm md:text-base items-center">
          <a href="#features" :class="['transition-colors font-bold', activeSection === 'features' ? 'text-memphis-coral' : 'hover:text-memphis-coral']">功能特色</a>
          <a href="#how-it-works" :class="['transition-colors font-bold', activeSection === 'how-it-works' ? 'text-memphis-coral' : 'hover:text-memphis-coral']">使用流程</a>
          <a href="#tech" :class="['transition-colors font-bold', activeSection === 'tech' ? 'text-memphis-coral' : 'hover:text-memphis-coral']">技术架构</a>
          <a href="#pricing" :class="['transition-colors font-bold', activeSection === 'pricing' ? 'text-memphis-coral' : 'hover:text-memphis-coral']">定价方案</a>
          <router-link
            v-if="!isLoggedIn"
            to="/auth"
            class="bg-memphis-coral text-white memphis-btn-primary px-4 py-2 text-sm"
          >
            登录 / 注册
          </router-link>
          <template v-else>
            <router-link
              to="/dashboard"
              class="flex items-center gap-2 border-4 border-black bg-memphis-coral text-white px-4 py-1.5 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all"
            >
              <div class="w-6 h-6 bg-white border-2 border-black flex items-center justify-center font-black text-[10px] text-memphis-coral">
                {{ avatarText }}
              </div>
              <span class="font-black text-xs">{{ displayName }}</span>
              <span class="font-mono text-[10px]">→ 仪表盘</span>
            </router-link>
          </template>
        </div>
        <!-- 移动端菜单按钮 -->
        <button class="md:hidden border-2 border-black p-2" @click="mobileMenu = !mobileMenu">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>
      <!-- 移动端菜单 -->
      <div v-if="mobileMenu" class="md:hidden mt-4 pb-4 border-t-2 border-black pt-4 flex flex-col gap-3 font-mono text-sm">
        <a href="#features" :class="['font-bold', activeSection === 'features' ? 'text-memphis-coral' : 'hover:text-memphis-coral']" @click="mobileMenu = false">功能特色</a>
        <a href="#how-it-works" :class="['font-bold', activeSection === 'how-it-works' ? 'text-memphis-coral' : 'hover:text-memphis-coral']" @click="mobileMenu = false">使用流程</a>
        <a href="#tech" :class="['font-bold', activeSection === 'tech' ? 'text-memphis-coral' : 'hover:text-memphis-coral']" @click="mobileMenu = false">技术架构</a>
        <a href="#pricing" :class="['font-bold', activeSection === 'pricing' ? 'text-memphis-coral' : 'hover:text-memphis-coral']" @click="mobileMenu = false">定价方案</a>
        <router-link v-if="!isLoggedIn" to="/auth" class="bg-memphis-coral text-white memphis-btn-primary px-4 py-2 text-sm w-fit">
          登录 / 注册
        </router-link>
        <router-link v-else to="/dashboard" class="bg-memphis-coral text-white memphis-btn-primary px-4 py-2 text-sm w-fit">
          {{ displayName }} → 仪表盘
        </router-link>
      </div>
    </nav>

    <!-- 主内容 -->
    <main class="flex-1">
      <slot />
    </main>

    <!-- 页脚 -->
    <footer class="bg-black text-white py-12 md:py-16 px-4 md:px-8 border-t-4 border-memphis-coral">
      <div class="max-w-screen-2xl mx-auto">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div class="md:col-span-2">
            <span class="font-black text-xl md:text-2xl flex items-center gap-2">
              <span class="inline-block w-8 h-8 bg-memphis-coral border-2 border-white" />
              AI模拟面试官
            </span>
            <p class="font-mono text-sm mt-4 text-gray-400 max-w-md">
              AI驱动的模拟面试、简历分析、职业测评一站式平台。助你斩获心仪Offer，规划职业未来。
            </p>
          </div>
          <div>
            <h4 class="font-black text-lg mb-4">快速链接</h4>
            <ul class="space-y-2 font-mono text-sm text-gray-400">
              <li><a href="#features" class="hover:text-memphis-coral transition-colors">功能特色</a></li>
              <li><a href="#how-it-works" class="hover:text-memphis-coral transition-colors">使用流程</a></li>
              <li><a href="#tech" class="hover:text-memphis-coral transition-colors">技术架构</a></li>
              <li><a href="#pricing" class="hover:text-memphis-coral transition-colors">定价方案</a></li>
            </ul>
          </div>
          <div>
            <h4 class="font-black text-lg mb-4">联系我们</h4>
            <ul class="space-y-2 font-mono text-sm text-gray-400">
              <li>support@ai-interview.com</li>
              <li>GitHub</li>
              <li>微信公众号</li>
            </ul>
          </div>
        </div>
        <div class="border-t border-gray-700 mt-8 pt-8 text-center font-mono text-xs text-gray-500">
          © 2026 AI模拟面试官与职业规划系统. All rights reserved.
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const mobileMenu = ref(false)
const activeSection = ref('')

const sectionIds = ['features', 'how-it-works', 'tech', 'pricing']

const isLoggedIn = computed(() => authStore.isAuthenticated)
const displayName = computed(() => authStore.user?.username || '用户')
const avatarText = computed(() => {
  const name = authStore.user?.username || '用'
  return name.charAt(0).toUpperCase()
})

function handleScroll() {
  const scrollY = window.scrollY + 120
  let current = ''
  for (const id of sectionIds) {
    const el = document.getElementById(id)
    if (el && el.offsetTop <= scrollY) {
      current = id
    }
  }
  activeSection.value = current
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true })
  handleScroll()
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>
