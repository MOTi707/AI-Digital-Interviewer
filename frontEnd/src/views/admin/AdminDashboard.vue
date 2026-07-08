<template>
  <div class="p-6 md:p-8 space-y-6 relative">
    <!-- 页面标题 -->
    <div class="flex items-center gap-4">
      <div class="w-3 h-12 bg-memphis-coral border-2 border-black" />
      <div>
        <h1 class="font-black text-3xl tracking-tight">数据概览</h1>
        <p class="font-mono text-xs text-black/60 mt-1">全平台实时数据统计</p>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
      <div
        v-for="(card, idx) in statCards"
        :key="card.label"
        :class="[
          'border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-5 md:p-6 relative overflow-hidden transition-all duration-200 hover:translate-x-[3px] hover:translate-y-[3px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]',
          card.bg
        ]"
      >
        <!-- 角落装饰 -->
        <div :class="['absolute -bottom-2 -right-2 w-16 h-16 opacity-10', idx === 0 ? 'bg-memphis-blue' : idx === 1 ? 'bg-memphis-yellow' : 'bg-memphis-purple']" style="transform: rotate(45deg)" />
        <div class="text-3xl mb-2">{{ card.icon }}</div>
        <div class="font-black text-4xl md:text-5xl tracking-tight">{{ card.value }}</div>
        <div class="font-mono text-xs text-black/60 mt-2 tracking-wide">{{ card.label }}</div>
        <div :class="['absolute top-0 right-0 w-4 h-4', card.dot]" />
      </div>
    </div>

    <!-- 二级统计 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
      <!-- 增长趋势 -->
      <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-5 md:p-6">
        <div class="flex items-center gap-2 mb-5">
          <div class="w-2 h-8 bg-memphis-teal border-2 border-black" />
          <h3 class="font-black text-xl tracking-tight">增长趋势</h3>
        </div>
        <div class="space-y-3">
          <div class="flex items-center justify-between border-4 border-black p-4 bg-memphis-cream hover:bg-memphis-yellow transition-all duration-200">
            <span class="font-black text-sm">今日新增用户</span>
            <span class="font-black text-2xl text-memphis-coral">{{ stats?.active_users_today ?? '-' }}</span>
          </div>
          <div class="flex items-center justify-between border-4 border-black p-4 bg-memphis-cream hover:bg-memphis-teal transition-all duration-200">
            <span class="font-black text-sm">本周新增用户</span>
            <span class="font-black text-2xl text-memphis-blue">{{ stats?.new_users_this_week ?? '-' }}</span>
          </div>
        </div>
      </div>

      <!-- 快捷操作 -->
      <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-5 md:p-6">
        <div class="flex items-center gap-2 mb-5">
          <div class="w-2 h-8 bg-memphis-orange border-2 border-black" />
          <h3 class="font-black text-xl tracking-tight">快捷操作</h3>
        </div>
        <div class="space-y-3">
          <router-link
            to="/admin/problems"
            class="flex items-center justify-between border-4 border-black p-4 bg-memphis-yellow font-black text-sm hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200"
          >
            <span>📝 管理题库</span>
            <span class="font-mono text-xs bg-black text-white px-2 py-1">{{ stats?.total_problems ?? 0 }} 题</span>
          </router-link>
          <router-link
            to="/admin/users"
            class="flex items-center justify-between border-4 border-black p-4 bg-memphis-blue text-white font-black text-sm hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200"
          >
            <span>👥 管理用户</span>
            <span class="font-mono text-xs bg-black text-white px-2 py-1">{{ stats?.total_users ?? 0 }} 人</span>
          </router-link>
          <router-link
            to="/admin/posts"
            class="flex items-center justify-between border-4 border-black p-4 bg-memphis-purple text-white font-black text-sm hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200"
          >
            <span>💬 审核帖子</span>
            <span class="font-mono text-xs bg-black text-white px-2 py-1">{{ stats?.total_posts ?? 0 }} 篇</span>
          </router-link>
        </div>
      </div>
    </div>

    <!-- 面试统计区 -->
    <div class="bg-memphis-coral border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-6 md:p-8 relative overflow-hidden">
      <svg class="absolute top-2 right-4 w-20 h-20 opacity-10" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="45" fill="white" />
      </svg>
      <div class="relative z-10">
        <h3 class="font-black text-xl text-white mb-1 tracking-tight">🎤 面试统计</h3>
        <p class="font-mono text-xs text-white/70 mb-4">全平台模拟面试会话总量</p>
        <div class="flex items-baseline gap-3">
          <span class="font-black text-6xl md:text-7xl text-white">{{ stats?.total_interviews ?? '-' }}</span>
          <span class="font-mono text-sm text-white/70">次面试</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useAdminStore } from '@/stores/admin'

const adminStore = useAdminStore()

const stats = computed(() => adminStore.stats)

const statCards = computed(() => [
  {
    icon: '👥',
    value: stats.value?.total_users ?? '-',
    label: '总用户数',
    bg: 'bg-white',
    dot: 'bg-memphis-blue',
  },
  {
    icon: '📝',
    value: stats.value?.total_problems ?? '-',
    label: '题库总量',
    bg: 'bg-white',
    dot: 'bg-memphis-yellow',
  },
  {
    icon: '💬',
    value: stats.value?.total_posts ?? '-',
    label: '面经帖子',
    bg: 'bg-white',
    dot: 'bg-memphis-purple',
  },
])

onMounted(() => {
  adminStore.fetchStats()
})
</script>
