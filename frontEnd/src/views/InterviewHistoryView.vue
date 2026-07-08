<template>
  <div class="min-h-screen bg-[#fef9ef]">
    <!-- 顶部导航 -->
    <nav class="sticky top-0 z-50 bg-white border-b-4 border-black px-6 py-3 flex items-center justify-between">
      <router-link to="/dashboard" class="font-black text-lg tracking-tight flex items-center gap-2">
        <span class="inline-block w-7 h-7 bg-[#ff006e] border-2 border-black" />
        <span>AI面试官</span>
      </router-link>
      <div class="flex gap-3">
        <router-link to="/dashboard" class="border-4 border-black bg-[#ff006e] text-white px-4 py-1.5 font-black text-xs shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all duration-200">
          + 新面试
        </router-link>
        <router-link to="/dashboard" class="border-4 border-black bg-white px-4 py-1.5 font-black text-xs shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all duration-200">
          ← 仪表盘
        </router-link>
      </div>
    </nav>

    <div class="max-w-4xl mx-auto px-6 py-8">
      <h1 class="font-black text-2xl md:text-3xl mb-6">面试历史</h1>

      <!-- 加载中 -->
      <div v-if="loading" class="text-center py-10 font-sans">加载中...</div>

      <!-- 历史记录列表 -->
      <div v-else-if="store.historyItems.length > 0" class="space-y-4">
        <button
          v-for="item in store.historyItems"
          :key="item.id"
          class="w-full text-left border-4 border-black bg-white shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-5 hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[3px] hover:translate-y-[3px] transition-all duration-200"
          @click="router.push(`/interview/report/${item.id}`)"
        >
          <div class="flex items-center justify-between">
            <div>
              <div class="font-black text-base flex items-center gap-2">
                {{ item.job_title }}
                <span
                  class="border-2 border-black px-1.5 py-0.5 font-black text-[10px] leading-none"
                  :class="getModeColor(item)"
                >{{ getModeLabel(item) }}</span>
              </div>
              <div class="font-sans text-xs text-gray-500 mt-1">
                {{ item.job_category }} · {{ formatDate(item.started_at) }}
              </div>
            </div>
            <div class="flex items-center gap-3">
              <!-- 等级 -->
              <div
                v-if="item.grade"
                class="border-2 border-black px-3 py-1 font-black text-sm"
                :class="getGradeColor(item.grade)"
              >
                {{ item.grade }}
              </div>
              <!-- 状态 -->
              <div class="border-2 border-black px-2 py-1 font-black text-xs" :class="getStatusColor(item.status)">
                {{ getStatusLabel(item.status) }}
              </div>
              <!-- 分数 -->
              <div v-if="item.total_score !== null" class="font-black text-sm">
                {{ item.total_score }}/{{ getMaxScore(item) }}分
              </div>
              <!-- 切屏警告 -->
              <div v-if="item.cheat_count > 0" class="text-xs text-red-500 font-black">
                ⚠️{{ item.cheat_count }}次切屏
              </div>
            </div>
          </div>
        </button>
      </div>

      <!-- 空状态 -->
      <div v-else class="border-4 border-black bg-white shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-8 text-center">
        <div class="text-4xl mb-3">📋</div>
        <p class="font-sans text-sm text-gray-600 mb-4">暂无面试记录</p>
        <button
          class="border-4 border-black bg-[#ff006e] text-white font-black px-6 py-2 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all duration-200"
          @click="router.push('/dashboard')"
        >
          开始第一次面试
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useInterviewStore } from '@/stores/interview'

const router = useRouter()
const store = useInterviewStore()
const loading = ref(true)

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function getGradeColor(grade: string): string {
  switch (grade) {
    case 'A': return 'bg-[#22c55e] text-white'
    case 'B': return 'bg-[#3a86ff] text-white'
    case 'C': return 'bg-[#ffbe0b]'
    default: return 'bg-[#ff006e] text-white'
  }
}

function getStatusColor(status: string): string {
  switch (status) {
    case 'completed': return 'bg-[#22c55e] text-white'
    case 'aborted': return 'bg-red-100 text-red-600'
    default: return 'bg-[#ffbe0b]'
  }
}

function getStatusLabel(status: string): string {
  switch (status) {
    case 'completed': return '已完成'
    case 'aborted': return '已中止'
    case 'in_progress': return '进行中'
    default: return status
  }
}

const roundLabels: Record<string, string> = {
  assessment: '综合素质',
  tech: '技术面',
  business: '业务面',
  ai_voice_3: 'AI面试',
  ai_voice_4: '综合面试',
}

function getModeLabel(item: { interview_mode: string; target_round: string | null }): string {
  if (item.interview_mode === 'full') return '全流程测试'
  if (item.interview_mode === 'single' && item.target_round) {
    return `单项·${roundLabels[item.target_round] || item.target_round}`
  }
  return '单项测试'
}

function getModeColor(item: { interview_mode: string }): string {
  return item.interview_mode === 'full'
    ? 'bg-[#3a86ff] text-white'
    : 'bg-[#ffbe0b]'
}

const roundMaxScore: Record<string, number> = {
  assessment: 100,
  tech: 20,
  business: 50,
  ai_voice_3: 90,
  ai_voice_4: 90,
}

function getMaxScore(item: { interview_mode: string; target_round: string | null }): number {
  if (item.interview_mode === 'full') return 350
  if (item.target_round && roundMaxScore[item.target_round]) return roundMaxScore[item.target_round]
  return 350
}

onMounted(async () => {
  try {
    await store.fetchHistory()
  } catch (e) {
    console.error('加载历史记录失败:', e)
  } finally {
    loading.value = false
  }
})
</script>
