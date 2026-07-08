<template>
  <div class="min-h-screen bg-[#fef9ef]">
    <!-- 顶部导航 -->
    <nav class="sticky top-0 z-50 bg-white border-b-4 border-black px-6 py-3 flex items-center justify-between">
      <router-link to="/dashboard" class="font-black text-lg tracking-tight flex items-center gap-2">
        <span class="inline-block w-7 h-7 bg-[#ff006e] border-2 border-black" />
        <span>AI面试官</span>
      </router-link>
      <div class="flex gap-3">
        <router-link to="/dashboard" class="border-4 border-black bg-white px-4 py-1.5 font-black text-xs shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all duration-200">
          ← 返回面试
        </router-link>
      </div>
    </nav>

    <div class="max-w-4xl mx-auto px-6 py-8">
      <!-- 加载中 -->
      <div v-if="loading" class="text-center py-20">
        <div class="font-black text-lg">加载评分报告中...</div>
      </div>

      <template v-else-if="report">
        <!-- 报告头部 -->
        <div class="border-4 border-black bg-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] p-6 mb-6 text-center">
          <div class="mb-3">
            <span
              class="inline-block border-2 border-black px-3 py-1 text-xs font-black"
              :class="isSingleMode ? 'bg-[#3a86ff] text-white' : 'bg-[#22c55e] text-white'"
            >{{ modeLabel }}</span>
          </div>
          <h1 class="font-black text-2xl md:text-3xl mb-2">面试评估报告</h1>
          <p class="font-sans text-sm text-gray-600 mb-4">
            {{ report.job_title }} · {{ report.job_category }}
          </p>

          <!-- 总分 + 等级 -->
          <div class="flex items-stretch justify-center gap-4 mb-4">
            <div class="border-4 border-black bg-[#fef9ef] px-8 py-3 flex items-center gap-2">
              <span class="font-black text-3xl">{{ report.total_score }}</span>
              <span class="font-black text-3xl">/</span>
              <span class="font-black text-3xl">{{ report.max_total }}分</span>
            </div>
            <div class="border-4 border-black px-10 py-3 font-black text-3xl flex items-center" :class="gradeColor">
              {{ report.grade }}
            </div>
          </div>

          <!-- 百分比进度条 -->
          <div class="flex items-center gap-3 max-w-sm mx-auto">
            <div class="border-2 border-black bg-white h-5 flex-1">
              <div
                class="h-full transition-all duration-1000"
                :class="gradeBarColor"
                :style="{ width: `${(report.total_score / report.max_total) * 100}%` }"
              />
            </div>
            <span class="font-black text-sm shrink-0">{{ ((report.total_score / report.max_total) * 100).toFixed(1) }}%</span>
          </div>
        </div>

        <!-- 能力雷达图 -->
        <div class="border-4 border-black bg-white shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-3 mb-6">
          <h3 class="font-black text-lg mb-1 text-center">能力雷达图</h3>
          <v-chart style="height: 350px; width: 100%;" :option="radarOption" autoresize />
        </div>

        <!-- 维度得分 -->
        <div class="border-4 border-black bg-white shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-5 mb-6">
          <h3 class="font-black text-lg mb-4">维度得分</h3>
          <div class="space-y-3">
            <div v-for="dim in radarDimensions" :key="dim.key">
              <div class="flex justify-between mb-1">
                <span class="font-black text-sm">{{ dim.label }}</span>
                <span class="font-black text-sm">{{ report.radar[dim.key as keyof typeof report.radar] }}%</span>
              </div>
              <div class="border-2 border-black bg-white h-3">
                <div
                  class="h-full transition-all duration-1000"
                  :class="dim.color"
                  :style="{ width: `${report.radar[dim.key as keyof typeof report.radar]}%` }"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- 改进建议 -->
        <div class="border-4 border-black bg-white shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-5 mb-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-black text-lg">改进建议</h3>
            <span class="border-2 border-black bg-[#8338ec] text-white text-xs font-black px-2 py-0.5">AI 生成</span>
          </div>
          <div class="space-y-3">
            <div
              v-for="(tip, idx) in report.suggestions"
              :key="idx"
              class="border-2 border-black p-4 bg-[#fef9ef]"
            >
              <div class="flex gap-3">
                <span class="font-black text-xl shrink-0 w-7 h-7 flex items-center justify-center border-2 border-black bg-[#ff006e] text-white">{{ idx + 1 }}</span>
                <p class="font-sans text-sm leading-relaxed">{{ tip }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- AI综合分析 -->
        <div v-if="report.ai_analysis" class="border-4 border-black bg-white shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-5 mb-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-black text-lg">AI 综合分析</h3>
            <span class="border-2 border-black bg-[#3a86ff] text-white text-xs font-black px-2 py-0.5">AI 生成</span>
          </div>
          <div class="border-2 border-black p-4 bg-[#fef9ef]">
            <p class="font-sans text-sm leading-relaxed whitespace-pre-line">{{ report.ai_analysis }}</p>
          </div>
          <p class="font-sans text-xs text-gray-500 mt-2 italic">* 本分析由 AI 自动生成，仅供参考，不构成专业职业建议。</p>
        </div>

        <!-- 操作按钮 -->
        <div class="flex gap-3 justify-center">
          <button
            class="border-4 border-black bg-[#ff006e] text-white font-black px-6 py-2 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all duration-200"
            @click="router.push('/dashboard')"
          >
            再来一次
          </button>
          <button
            class="border-4 border-black bg-white font-black px-6 py-2 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all duration-200"
            @click="router.push('/interview/history')"
          >
            面试历史
          </button>
        </div>
      </template>

      <!-- 无报告（答题不足） -->
      <div v-else class="border-4 border-black bg-white shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-8 text-center">
        <div class="text-4xl mb-3">📝</div>
        <h3 class="font-black text-xl mb-2">暂无评分报告</h3>
        <p class="font-sans text-sm text-gray-600 mb-4">{{ errorMsg || '答题数量不足3题，系统无法生成评分报告。建议重新尝试面试。' }}</p>
        <button class="border-4 border-black bg-[#ff006e] text-white font-black px-6 py-2 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all duration-200" @click="router.push('/dashboard')">
          返回面试
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { RadarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useInterviewStore, type InterviewReport } from '@/stores/interview'

use([RadarChart, TitleComponent, TooltipComponent, CanvasRenderer])

const route = useRoute()
const router = useRouter()
const store = useInterviewStore()

const report = ref<InterviewReport | null>(null)
const loading = ref(true)
const errorMsg = ref('')

const sessionId = computed(() => route.params.id as string)

const radarDimensions = [
  { key: 'professional', label: '专业能力', color: 'bg-[#ff006e]' },
  { key: 'logic', label: '逻辑思维', color: 'bg-[#3a86ff]' },
  { key: 'communication', label: '沟通表达', color: 'bg-[#8338ec]' },
  { key: 'match', label: '岗位匹配度', color: 'bg-[#22c55e]' },
]

const roundLabelMap: Record<string, string> = {
  assessment: '综合素质测评', tech: '一面·技术面', business: '二面·业务面',
  ai_voice_3: '三面·AI面试', ai_voice_4: '四面·综合面试',
}
const isSingleMode = computed(() => report.value?.interview_mode === 'single')
const modeLabel = computed(() => {
  if (!report.value) return ''
  if (report.value.interview_mode === 'single' && report.value.target_round) {
    return `单轮练习 · ${roundLabelMap[report.value.target_round] || report.value.target_round}`
  }
  return '全流程面试'
})

const gradeColor = computed(() => {
  if (!report.value) return 'bg-white'
  switch (report.value.grade) {
    case 'A': return 'bg-[#22c55e] text-white'
    case 'B': return 'bg-[#3a86ff] text-white'
    case 'C': return 'bg-[#ffbe0b]'
    default: return 'bg-[#ff006e] text-white'
  }
})

const gradeBarColor = computed(() => {
  if (!report.value) return 'bg-gray-300'
  const pct = (report.value.total_score / report.value.max_total) * 100
  if (pct >= 85) return 'bg-[#22c55e]'
  if (pct >= 70) return 'bg-[#3a86ff]'
  if (pct >= 55) return 'bg-[#ffbe0b]'
  return 'bg-[#ff006e]'
})

const radarOption = computed(() => ({
  radar: {
    indicator: [
      { name: '专业能力', max: 100 },
      { name: '逻辑思维', max: 100 },
      { name: '沟通表达', max: 100 },
      { name: '岗位匹配', max: 100 },
    ],
    shape: 'polygon',
    splitNumber: 4,
    radius: '75%',
    axisName: { color: '#000', fontWeight: 'bold', fontSize: 16 },
  },
  series: [{
    type: 'radar',
    data: [{
      value: report.value ? [
        report.value.radar.professional,
        report.value.radar.logic,
        report.value.radar.communication,
        report.value.radar.match,
      ] : [0, 0, 0, 0],
      name: '面试评分',
      areaStyle: { color: 'rgba(255, 0, 110, 0.2)' },
      lineStyle: { color: '#ff006e', width: 2 },
      itemStyle: { color: '#ff006e' },
    }],
  }],
  tooltip: {},
}))

onMounted(async () => {
  try {
    report.value = await store.fetchReport(sessionId.value)
  } catch (e) {
    console.error('加载报告失败:', e)
    errorMsg.value = (e as Error).message || '加载报告失败'
  } finally {
    loading.value = false
  }
})
</script>
