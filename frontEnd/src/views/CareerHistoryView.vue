<template>
  <div class="min-h-screen bg-memphis-cream">
    <!-- 顶部导航 -->
    <nav class="bg-white border-b-4 border-black px-6 py-3 flex items-center justify-between">
      <router-link to="/dashboard" class="font-black text-lg tracking-tight flex items-center gap-2">
        <span class="inline-block w-7 h-7 bg-memphis-coral border-2 border-black" />
        <span>AI面试官</span>
      </router-link>
      <button
        class="px-4 py-1.5 font-black text-xs border-4 border-black bg-white hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200"
        @click="router.push('/dashboard')"
      >
        ← 返回仪表盘
      </button>
    </nav>

    <div class="max-w-4xl mx-auto px-4 py-8">
      <!-- 标题 -->
      <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-6 mb-6">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-memphis-yellow border-4 border-black flex items-center justify-center">
            <span class="text-lg">📋</span>
          </div>
          <div>
            <h1 class="font-black text-2xl tracking-tight">测评历史</h1>
            <p class="font-mono text-sm text-gray-700">查看你所有的职业测评记录</p>
          </div>
        </div>
      </div>

      <!-- 快速入口 -->
      <div class="grid grid-cols-3 gap-4 mb-6">
        <button
          v-for="test in testTypes"
          :key="test.type"
          class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-4 hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[3px] hover:translate-y-[3px] transition-all duration-200 text-left"
          @click="router.push(`/career/test/${test.type}`)"
        >
          <div class="text-2xl mb-1">{{ test.icon }}</div>
          <div class="font-black text-sm">{{ test.label }}</div>
          <div class="font-mono text-xs text-gray-600 mt-0.5">{{ test.desc }}</div>
        </button>
      </div>

      <!-- 加载中 -->
      <div v-if="store.loading" class="text-center py-12">
        <div class="font-black text-xl text-memphis-purple">加载中...</div>
      </div>

      <!-- 历史记录列表 -->
      <div v-else-if="store.history.items.length > 0" class="space-y-4">
        <div
          v-for="item in store.history.items"
          :key="item.id"
          class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-5 flex items-center justify-between hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[3px] hover:translate-y-[3px] transition-all duration-200 cursor-pointer"
          @click="router.push(`/career/result/${item.id}`)"
        >
          <div class="flex items-center gap-4">
            <div
              class="w-10 h-10 border-4 border-black flex items-center justify-center text-lg"
              :class="typeIcon(item.type).bg"
            >
              {{ typeIcon(item.type).icon }}
            </div>
            <div>
              <div class="font-black text-sm">{{ typeLabel(item.type) }}</div>
              <div class="font-mono text-xs text-gray-600 mt-0.5">{{ formatDate(item.created_at) }}</div>
            </div>
          </div>
          <div class="text-right">
            <div class="font-black text-sm" :class="resultColor(item.type)">
              {{ resultSummary(item) }}
            </div>
            <button
              class="mt-1 px-3 py-1 font-black text-xs border-2 border-black bg-memphis-yellow hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all"
              @click.stop="router.push(`/career/result/${item.id}`)"
            >
              查看详情 →
            </button>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-12 text-center">
        <div class="text-5xl mb-4">📝</div>
        <div class="font-black text-xl mb-2">暂无测评记录</div>
        <div class="font-mono text-sm text-gray-600 mb-6">选择一个测评开始你的职业探索之旅</div>
        <button
          class="px-6 py-3 font-black text-sm border-4 border-black bg-memphis-coral text-white shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[3px] hover:translate-y-[3px] transition-all duration-200"
          @click="router.push('/career/test/holland')"
        >
          🚀 开始第一次测评
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCareerStore } from '@/stores/career'
import type { AssessmentRecord } from '@/stores/career'

const router = useRouter()
const store = useCareerStore()

const testTypes = [
  { type: 'holland', label: 'Holland 测评', desc: '职业兴趣探索', icon: '🧭' },
  { type: 'mbti', label: 'MBTI 测评', desc: '性格类型分析', icon: '🧠' },
  { type: 'career_values', label: '价值观测评', desc: '核心价值发现', icon: '💎' },
]

function typeLabel(type: string): string {
  return { holland: 'Holland 六维度', mbti: 'MBTI 性格', career_values: '职业价值观' }[type] || type
}

function typeIcon(type: string) {
  const map: Record<string, { icon: string; bg: string }> = {
    holland: { icon: '🧭', bg: 'bg-memphis-yellow' },
    mbti: { icon: '🧠', bg: 'bg-memphis-purple' },
    career_values: { icon: '💎', bg: 'bg-memphis-coral' },
  }
  return map[type] || { icon: '📝', bg: 'bg-memphis-blue' }
}

function resultColor(type: string): string {
  return { holland: 'text-memphis-purple', mbti: 'text-memphis-blue', career_values: 'text-memphis-coral' }[type] || 'text-black'
}

function resultSummary(item: AssessmentRecord): string {
  const r = item.result as Record<string, unknown>
  if (item.type === 'holland') return `代码: ${r.holland_code || '-'}`
  if (item.type === 'mbti') return `${r.type || '-'}`
  if (item.type === 'career_values') {
    const core = (r.core_values || []) as string[]
    const nameMap: Record<string, string> = { achievement: '成就感', reward: '经济报酬', autonomy: '自主性', contribution: '社会贡献', relationship: '人际关系', environment: '工作环境' }
    return core.map((c: string) => nameMap[c] || c).join(' / ')
  }
  return '-'
}

function formatDate(dt: string) {
  return new Date(dt).toLocaleString('zh-CN')
}

onMounted(() => {
  store.fetchHistory()
})
</script>
