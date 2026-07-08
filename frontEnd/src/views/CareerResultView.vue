<template>
  <div class="min-h-screen bg-memphis-cream">
    <!-- 顶部导航 -->
    <nav class="bg-white border-b-4 border-black px-6 py-3 flex items-center justify-between">
      <router-link to="/dashboard" class="font-black text-lg tracking-tight flex items-center gap-2">
        <span class="inline-block w-7 h-7 bg-memphis-coral border-2 border-black" />
        <span>AI面试官</span>
      </router-link>
      <div class="flex gap-2">
        <button
          class="px-4 py-1.5 font-black text-xs border-4 border-black bg-memphis-yellow hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200"
          @click="router.push('/career/history')"
        >📋 测评历史</button>
        <button
          class="px-4 py-1.5 font-black text-xs border-4 border-black bg-white hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200"
          @click="router.push('/dashboard')"
        >← 返回仪表盘</button>
      </div>
    </nav>

    <!-- 加载中 -->
    <div v-if="loading" class="flex items-center justify-center py-32">
      <div class="font-black text-2xl text-memphis-purple">加载结果中...</div>
    </div>

    <!-- 结果主体 -->
    <div v-else-if="record" class="max-w-5xl mx-auto px-4 py-8">

      <!-- 摘要卡 -->
      <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-6 mb-6">
        <div class="flex items-center gap-3 mb-3">
          <div class="w-10 h-10 bg-memphis-purple border-4 border-black flex items-center justify-center">
            <span class="text-lg">🎯</span>
          </div>
          <div>
            <div class="font-mono text-xs text-gray-600">{{ typeLabel }}</div>
            <h1 class="font-black text-2xl tracking-tight">测评结果</h1>
          </div>
        </div>
        <div class="font-black text-lg md:text-xl text-memphis-coral mt-3">{{ record.summary }}</div>
        <div class="font-mono text-xs text-gray-600 mt-2">{{ formatDate(record.created_at) }}</div>
      </div>

      <!-- ═══ Holland 雷达图 ═══ -->
      <div v-if="record.type === 'holland'" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- 雷达图 -->
          <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-6 flex items-center justify-center">
            <div v-html="radarSvg" class="w-full" style="max-width:400px" />
          </div>
          <!-- 霍兰德代码 + 职业建议 -->
          <div class="space-y-4">
            <div class="bg-memphis-yellow border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-5">
              <div class="font-black text-sm mb-1">你的霍兰德代码</div>
              <div class="font-black text-5xl tracking-wider">{{ hollandCode }}</div>
              <div class="flex gap-2 mt-3">
                <span v-for="d in hollandTop3" :key="d.code"
                  class="px-3 py-1 font-black text-xs border-2 border-black bg-white">
                  {{ d.code }} · {{ d.name.replace(/ \(.+\)/, '') }}
                </span>
              </div>
            </div>
            <div v-for="item in hollandTop3" :key="item.code"
              class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-4">
              <div class="font-black text-sm mb-1">{{ item.name }}</div>
              <div class="font-mono text-xs text-gray-700 mb-2">{{ item.desc }}</div>
              <div class="flex flex-wrap gap-1">
                <span v-for="c in item.careers" :key="c"
                  class="px-2 py-0.5 font-mono text-xs border-2 border-black bg-memphis-cream">{{ c }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ═══ MBTI 双向条形图 ═══ -->
      <div v-else-if="record.type === 'mbti'" class="space-y-6">
        <!-- 类型卡片 -->
        <div class="bg-memphis-purple border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-8 text-center text-white">
          <img v-if="mbtiAvatarUrl" :src="mbtiAvatarUrl" :alt="mbtiType" class="mx-auto mb-4 h-48 md:h-56 drop-shadow-[3px_3px_0px_rgba(0,0,0,0.8)]"  />
          <div class="font-black text-6xl md:text-8xl tracking-wider mb-2">{{ mbtiType }}</div>
          <div class="font-black text-2xl">{{ mbtiInfo?.name }}</div>
          <p class="font-mono text-sm mt-3 max-w-lg mx-auto">{{ mbtiInfo?.desc }}</p>
        </div>
        <!-- 双向条形图 -->
        <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-6">
          <h2 class="font-black text-xl mb-4">📊 四维度倾向分布</h2>
          <v-chart :option="mbtiChartOption" autoresize class="w-full" style="height: 360px" />
        </div>
        <!-- 优势 + 职业推荐 -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-5">
            <h3 class="font-black text-lg mb-3">💪 核心优势</h3>
            <div class="space-y-2">
              <div v-for="s in mbtiStrengths" :key="s"
                class="flex items-center gap-2 border-2 border-black p-2 bg-memphis-cream">
                <span class="w-2 h-2 bg-memphis-coral border border-black" />
                <span class="font-mono text-sm">{{ s }}</span>
              </div>
            </div>
          </div>
          <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-5">
            <h3 class="font-black text-lg mb-3">💼 适合职业</h3>
            <div class="flex flex-wrap gap-2">
              <span v-for="career in mbtiCareers" :key="career"
                class="px-3 py-1 font-black text-xs border-2 border-black bg-memphis-yellow">{{ career }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ═══ 职业价值观 环形图 + 词云 ═══ -->
      <div v-else-if="record.type === 'career_values'" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- 环形图 -->
          <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-6 flex flex-col items-center">
            <h2 class="font-black text-lg mb-4 self-start">💎 价值观权重分布</h2>
            <div v-html="donutSvg" class="w-full" style="max-width:500px" />
          </div>
          <!-- 词云 + 核心价值观 -->
          <div class="space-y-4">
            <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-6">
              <h2 class="font-black text-lg mb-4">🌐 价值观因子</h2>
              <div v-html="wordcloudSvg" class="w-full" />
            </div>
            <div v-for="dim in cvCoreDims" :key="dim.code"
              class="border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-4"
              :class="dim.is_core ? 'bg-memphis-coral' : 'bg-white'">
              <div class="flex items-center gap-2 mb-1">
                <span class="font-black text-lg" :class="dim.is_core ? 'text-white' : ''">{{ dim.name }}</span>
                <span v-if="dim.is_core" class="px-2 py-0.5 font-black text-xs border-2 border-black bg-white">核心</span>
              </div>
              <div class="font-mono text-xs mb-1" :class="dim.is_core ? 'text-white/80' : 'text-gray-600'">{{ dim.desc }}</div>
              <div class="font-black text-sm" :class="dim.is_core ? 'text-white' : ''">得分：{{ dim.avg_score }} / 5.00</div>
            </div>
          </div>
        </div>
        <!-- 职业发展建议 -->
        <div class="bg-memphis-yellow border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-5">
          <h3 class="font-black text-lg mb-2">💡 职业发展建议</h3>
          <p class="font-mono text-sm">
            你最重视的 <strong>{{ cvCoreNames }}</strong> 是你职业选择的核心驱动力。
            建议优先考虑能够满足这些价值观的工作环境和岗位，在求职面试中也可以将这些作为评估公司文化匹配度的重要参考维度。
          </p>
        </div>
      </div>

      <!-- ═══ AI 岗位匹配推荐 ═══ -->
      <div class="mt-8 space-y-4">
        <!-- 区块标题 -->
        <div class="bg-memphis-coral border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-5">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-white border-4 border-black flex items-center justify-center">
              <span class="text-lg">🤖</span>
            </div>
            <div>
              <h2 class="font-black text-xl tracking-tight text-white">AI 岗位匹配推荐</h2>
              <p class="font-mono text-xs text-white/80">基于测评结果 + 简历技能智能分析</p>
            </div>
          </div>
        </div>

        <!-- 加载中 -->
        <div v-if="store.recommendation.loading && store.recommendation.jobs.length === 0"
          class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-8 text-center">
          <div class="inline-block w-8 h-8 border-4 border-black border-t-transparent animate-spin mb-3" />
          <div class="font-black text-sm">AI 正在分析你的测评结果...</div>
          <div class="font-mono text-xs text-gray-600 mt-1">首次加载可能需要 10-20 秒</div>
        </div>

        <!-- 错误 -->
        <div v-else-if="store.recommendation.error"
          class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-5">
          <div class="font-black text-sm text-memphis-coral">❌ 推荐加载失败</div>
          <div class="font-mono text-xs text-gray-600 mt-1">{{ store.recommendation.error }}</div>
          <button
            class="mt-3 px-4 py-1.5 font-black text-xs border-4 border-black bg-memphis-yellow hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200"
            @click="triggerRecommendation">🔄 重试</button>
        </div>

        <!-- 推荐岗位卡片网格 -->
        <div v-if="store.recommendation.jobs.length > 0" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="(job, idx) in store.recommendation.jobs" :key="idx"
              class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-5 flex flex-col gap-3">
              <!-- 岗位名 + 排名标号 -->
              <div class="flex items-start justify-between gap-2">
                <h3 class="font-black text-base leading-tight">{{ job.title }}</h3>
                <span class="px-2 py-0.5 font-black text-xs border-2 border-black bg-memphis-purple text-white flex-shrink-0">
                  #{{ idx + 1 }}
                </span>
              </div>
              <!-- 匹配度进度条 -->
              <div>
                <div class="flex items-center justify-between mb-1">
                  <span class="font-mono text-xs">匹配度</span>
                  <span class="font-black text-sm text-memphis-coral">{{ job.match }}%</span>
                </div>
                <div class="h-3 bg-memphis-cream border-2 border-black relative">
                  <div
                    class="h-full border-2 border-black"
                    :class="job.match >= 85 ? 'bg-memphis-coral' : job.match >= 70 ? 'bg-memphis-yellow' : 'bg-memphis-teal'"
                    :style="{ width: `${Math.min(job.match, 100)}%` }"
                  />
                </div>
              </div>
              <!-- 匹配理由 -->
              <p class="font-mono text-xs text-gray-700 flex-1">{{ job.reason }}</p>
              <!-- 薪资范围 -->
              <div class="flex items-center gap-2 pt-1 border-t-2 border-black">
                <span class="font-mono text-xs">💰</span>
                <span class="font-black text-sm text-memphis-purple">{{ job.salary_range }}</span>
              </div>
            </div>
          </div>

          <!-- 面试准备建议 -->
          <div v-if="store.recommendation.prep_tips.length > 0 || store.recommendation.loading"
            class="bg-memphis-yellow border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-6">
            <h3 class="font-black text-lg mb-4">📝 面试准备重点建议</h3>
            <div class="space-y-4">
              <div v-for="(group, gi) in store.recommendation.prep_tips" :key="gi"
                class="border-2 border-black bg-white p-4">
                <div class="font-black text-sm mb-2 flex items-center gap-2">
                  <span class="w-5 h-5 bg-memphis-coral border-2 border-black flex items-center justify-center font-black text-xs text-white">{{ gi + 1 }}</span>
                  {{ group.category }}
                </div>
                <ul class="space-y-1.5 pl-7">
                  <li v-for="(tip, ti) in group.tips" :key="ti"
                    class="font-mono text-xs text-gray-700 flex items-start gap-2">
                    <span class="mt-0.5 w-1.5 h-1.5 bg-memphis-coral border border-black flex-shrink-0" />
                    {{ tip }}
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <!-- 仍在加载提示 -->
          <div v-if="store.recommendation.loading"
            class="flex items-center gap-2 font-mono text-xs text-gray-600">
            <span class="inline-block w-3 h-3 border-2 border-black border-t-transparent animate-spin" />
            正在加载面试准备建议...
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="flex gap-4 mt-8 mb-12">
        <button
          class="flex-1 py-3 border-4 border-black font-black text-sm bg-memphis-yellow shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[3px] hover:translate-y-[3px] transition-all duration-200"
          @click="retake">🔄 重新测评</button>
        <button
          class="flex-1 py-3 border-4 border-black font-black text-sm bg-white shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[3px] hover:translate-y-[3px] transition-all duration-200"
          @click="router.push('/career/history')">📋 查看历史</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import {
  GridComponent, TooltipComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useRoute, useRouter } from 'vue-router'
import { useCareerStore } from '@/stores/career'
import type { AssessmentRecord } from '@/stores/career'

const route = useRoute()
const router = useRouter()
const store = useCareerStore()

const loading = ref(true)
const record = ref<AssessmentRecord | null>(null)

const typeLabels: Record<string, string> = {
  holland: 'Holland 六维度职业兴趣测评',
  mbti: 'MBTI 性格类型测评',
  career_values: '职业价值观测评',
}
const typeLabel = computed(() => typeLabels[record.value?.type || ''] || '职业测评')
function formatDate(dt: string) { return new Date(dt).toLocaleString('zh-CN') }

use([BarChart, GridComponent, TooltipComponent, CanvasRenderer])

const COLORS = ['#ff006e', '#ffbe0b', '#3a86ff', '#8338ec', '#fb5607', '#00f5d4']

// ─── Holland ─────────────────────────────────────────
const hResult = computed(() => record.value?.result as Record<string, unknown> | undefined)
const hollandCode = computed(() => (hResult.value?.holland_code as string) || '')
const hollandTop3 = computed(() =>
  ((hResult.value?.top3 || []) as Array<{ code: string; name: string; desc: string; score: number; careers: string[] }>))
const hollandScores = computed(() => (hResult.value?.scores || {}) as Record<string, number>)

const radarSvg = computed(() => {
  const W = 400, H = 400, cx = W / 2, cy = H / 2, R = 140
  const dims = [
    { code: 'R', name: '现实型 R' }, { code: 'I', name: '研究型 I' },
    { code: 'A', name: '艺术型 A' }, { code: 'S', name: '社会型 S' },
    { code: 'E', name: '企业型 E' }, { code: 'C', name: '常规型 C' },
  ]
  const scores = hollandScores.value
  const maxS = Math.max(...Object.values(scores), 1) || 1
  const angles = dims.map((_, i) => -Math.PI / 2 + (2 * Math.PI / 6) * i)
  const pt = (a: number, r: number) =>
    `${(cx + r * Math.cos(a)).toFixed(1)},${(cy + r * Math.sin(a)).toFixed(1)}`

  let s = `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">`
  // 网格
  for (const lv of [0.2, 0.4, 0.6, 0.8, 1.0]) {
    const pts = angles.map(a => pt(a, R * lv)).join(' ')
    s += `<polygon points="${pts}" fill="none" stroke="#000" stroke-width="1" stroke-dasharray="3,3" opacity="0.15"/>`
  }
  // 轴线
  for (const a of angles) {
    s += `<line x1="${cx}" y1="${cy}" x2="${(cx + R * Math.cos(a)).toFixed(1)}" y2="${(cy + R * Math.sin(a)).toFixed(1)}" stroke="#000" stroke-width="1" opacity="0.2"/>`
  }
  // 数据多边形
  const dataPts = dims.map((d, i) => pt(angles[i], R * ((scores[d.code] || 0) / maxS))).join(' ')
  s += `<polygon points="${dataPts}" fill="#8338ec" fill-opacity="0.3" stroke="#8338ec" stroke-width="3"/>`
  // 数据点 + 标签
  dims.forEach((d, i) => {
    const a = angles[i]
    const dx = cx + (R * (scores[d.code] || 0) / maxS) * Math.cos(a)
    const dy = cy + (R * (scores[d.code] || 0) / maxS) * Math.sin(a)
    s += `<circle cx="${dx.toFixed(1)}" cy="${dy.toFixed(1)}" r="6" fill="${COLORS[i]}" stroke="#000" stroke-width="2"/>`
    const lx = cx + (R + 36) * Math.cos(a), ly = cy + (R + 36) * Math.sin(a)
    const anc = Math.abs(Math.cos(a)) < 0.15 ? 'middle' : Math.cos(a) > 0 ? 'start' : 'end'
    s += `<text x="${lx.toFixed(1)}" y="${(ly - 7).toFixed(1)}" text-anchor="${anc}" font-weight="900" font-size="13" fill="#000">${d.name}</text>`
    s += `<text x="${lx.toFixed(1)}" y="${(ly + 10).toFixed(1)}" text-anchor="${anc}" font-weight="900" font-size="15" fill="${COLORS[i]}">${scores[d.code] || 0}分</text>`
  })
  s += '</svg>'
  return s
})

// ─── MBTI ────────────────────────────────────────────
const mbtiResult = computed(() => record.value?.result as Record<string, unknown> | undefined)
const mbtiType = computed(() => (mbtiResult.value?.type as string) || '')
const mbtiInfo = computed(() => mbtiResult.value?.type_info as Record<string, unknown> | undefined)
const mbtiStrengths = computed(() => (mbtiInfo.value?.strengths || []) as string[])
const mbtiCareers = computed(() => (mbtiInfo.value?.careers || []) as string[])

// 16personalities 角色插图映射（本地 SVG 动画）
const MBTI_LOCAL_FILES: Record<string, string> = {
  INTJ: 'intj-architect.svg', INTP: 'intp-logician.svg',
  ENTJ: 'entj-commander.svg', ENTP: 'entp-debater.svg',
  INFJ: 'infj-advocate.svg', INFP: 'infp-mediator.svg',
  ENFJ: 'enfj-protagonist.svg', ENFP: 'enfp-campaigner.svg',
  ISTJ: 'istj-logistician.svg', ISFJ: 'isfj-defender.svg',
  ESTJ: 'estj-executive.svg', ESFJ: 'esfj-consul.svg',
  ISTP: 'istp-virtuoso.svg', ISFP: 'isfp-adventurer.svg',
  ESTP: 'estp-entrepreneur.svg', ESFP: 'esfp-entertainer.svg',
}
const mbtiAvatarUrl = computed(() => {
  const file = MBTI_LOCAL_FILES[mbtiType.value]
  return file ? `/mbti/${file}` : ''
})
const mbtiDimensions = computed(() =>
  (mbtiResult.value?.dimensions || {}) as Record<string, { left: { letter: string; score: number }; right: { letter: string; score: number }; winner: string }>)

const mbtiChartOption = computed(() => {
  const dims = mbtiDimensions.value
  const categories = Object.keys(dims)
  const dimMeta: Record<string, { left: string; right: string }> = {
    EI: { left: '外向 E', right: '内向 I' },
    SN: { left: '感觉 S', right: '直觉 N' },
    TF: { left: '思考 T', right: '情感 F' },
    JP: { left: '判断 J', right: '知觉 P' },
  }
  // 每个维度统一一个颜色，左右柱子同色
  const dimColor: Record<string, string> = {
    EI: '#ff006e', SN: '#ffbe0b', TF: '#8338ec', JP: '#3a86ff',
  }
  const leftData = categories.map(key => {
    const dim = dims[key]
    const total = dim.left.score + dim.right.score || 1
    return -Math.round((dim.left.score / total) * 100)
  })
  const rightData = categories.map(key => {
    const dim = dims[key]
    const total = dim.left.score + dim.right.score || 1
    return Math.round((dim.right.score / total) * 100)
  })
  const leftLabels = categories.map(k => dimMeta[k]?.left || k)
  const rightLabels = categories.map(k => dimMeta[k]?.right || k)

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const idx = params[0].dataIndex
        const key = categories[idx]
        const dim = dims[key]
        const lPct = Math.abs(params[0].value)
        const rPct = params[1].value
        const m = dimMeta[key]
        return `<b>${m.left} / ${m.right}</b><br/>${m.left}：${lPct}%<br/>${m.right}：${rPct}%<br/>倾向：<b>${dim.winner}</b>`
      },
    },
    grid: { left: 90, right: 90, top: 10, bottom: 40 },
    xAxis: {
      type: 'value', min: -100, max: 100,
      axisLabel: {
        fontWeight: 900, fontSize: 11,
        formatter: (v: number) => Math.abs(v) + '%',
      },
      splitLine: { lineStyle: { type: 'dashed', color: '#000', opacity: 0.1 } },
      axisLine: { lineStyle: { color: '#000', width: 2 } },
    },
    yAxis: [
      {
        type: 'category', data: leftLabels, position: 'left',
        axisLabel: { fontWeight: 900, fontSize: 13, color: '#000' },
        axisLine: { lineStyle: { color: '#000', width: 2 } },
        axisTick: { show: false },
      },
      {
        type: 'category', data: rightLabels, position: 'right',
        axisLabel: { fontWeight: 900, fontSize: 13, color: '#000' },
        axisLine: { show: false }, axisTick: { show: false },
      },
    ],
    series: [
      {
        name: 'left', type: 'bar', stack: 'total',
        data: leftData, barWidth: 28,
        itemStyle: {
          color: (p: any) => dimColor[categories[p.dataIndex]] || '#ff006e',
          borderColor: '#000', borderWidth: 2,
        },
        label: {
          show: true, position: 'left', fontWeight: 900, fontSize: 12,
          formatter: (p: any) => Math.abs(p.value) + '%',
          color: (p: any) => dimColor[categories[p.dataIndex]] || '#ff006e',
        },
      },
      {
        name: 'right', type: 'bar', stack: 'total',
        data: rightData, barWidth: 28,
        itemStyle: {
          color: (p: any) => dimColor[categories[p.dataIndex]] || '#ff006e',
          borderColor: '#000', borderWidth: 2,
        },
        label: {
          show: true, position: 'right', fontWeight: 900, fontSize: 12,
          formatter: (p: any) => p.value + '%',
          color: (p: any) => dimColor[categories[p.dataIndex]] || '#ff006e',
        },
      },
    ],
  }
})

// ─── Career Values ───────────────────────────────────
const cvResult = computed(() => record.value?.result as Record<string, unknown> | undefined)
const cvDimensions = computed(() =>
  (cvResult.value?.dimensions || []) as Array<{ code: string; name: string; desc: string; avg_score: number; is_core: boolean }>)
const cvCoreDims = computed(() => cvDimensions.value.filter(d => d.is_core))
const cvCoreNames = computed(() => cvCoreDims.value.map(d => d.name).join(' 与 '))

const donutSvg = computed(() => {
  const W = 500, H = 440, cx = W / 2, cy = H / 2, outerR = 120, innerR = 70
  const dims = cvDimensions.value
  const total = dims.reduce((s, d) => s + d.avg_score, 0) || 1
  let curAngle = -Math.PI / 2
  let s = `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" style="overflow:visible">`

  dims.forEach((dim, i) => {
    const pct = dim.avg_score / total
    const sliceAngle = pct * 2 * Math.PI
    const endAngle = curAngle + sliceAngle
    const la = sliceAngle > Math.PI ? 1 : 0
    const x1o = cx + outerR * Math.cos(curAngle), y1o = cy + outerR * Math.sin(curAngle)
    const x2o = cx + outerR * Math.cos(endAngle), y2o = cy + outerR * Math.sin(endAngle)
    const x1i = cx + innerR * Math.cos(endAngle), y1i = cy + innerR * Math.sin(endAngle)
    const x2i = cx + innerR * Math.cos(curAngle), y2i = cy + innerR * Math.sin(curAngle)
    s += `<path d="M${x1o.toFixed(2)},${y1o.toFixed(2)} A${outerR},${outerR} 0 ${la} 1 ${x2o.toFixed(2)},${y2o.toFixed(2)} L${x1i.toFixed(2)},${y1i.toFixed(2)} A${innerR},${innerR} 0 ${la} 0 ${x2i.toFixed(2)},${y2i.toFixed(2)} Z" fill="${COLORS[i % 6]}" stroke="#000" stroke-width="3"/>`
    // 标签 - 引线 + 文字
    const midA = curAngle + sliceAngle / 2
    const labelR = outerR + 38
    const lx = cx + labelR * Math.cos(midA), ly = cy + labelR * Math.sin(midA)
    const anc = Math.cos(midA) > 0.1 ? 'start' : Math.cos(midA) < -0.1 ? 'end' : 'middle'
    // 引线起点（扇形边缘）
    const lineStart = outerR + 4
    const lsx = cx + lineStart * Math.cos(midA), lsy = cy + lineStart * Math.sin(midA)
    s += `<line x1="${lsx.toFixed(1)}" y1="${lsy.toFixed(1)}" x2="${lx.toFixed(1)}" y2="${ly.toFixed(1)}" stroke="#000" stroke-width="1.5"/>`
    s += `<text x="${lx.toFixed(1)}" y="${(ly + 4).toFixed(1)}" text-anchor="${anc}" font-weight="900" font-size="13" fill="#000">${dim.name} ${Math.round(pct * 100)}%</text>`
    curAngle = endAngle
  })
  // 中心
  s += `<circle cx="${cx}" cy="${cy}" r="${innerR - 6}" fill="#fef9ef" stroke="#000" stroke-width="2"/>`
  s += `<text x="${cx}" y="${cy - 6}" text-anchor="middle" font-weight="900" font-size="15" fill="#000">核心</text>`
  s += `<text x="${cx}" y="${cy + 14}" text-anchor="middle" font-weight="900" font-size="15" fill="#ff006e">价值观</text>`
  s += '</svg>'
  return s
})

const wordcloudSvg = computed(() => {
  const W = 480
  const dims = [...cvDimensions.value].sort((a, b) => b.avg_score - a.avg_score)
  const maxScore = Math.max(...dims.map(d => d.avg_score), 1) || 1
  // 中文字符宽度约等于 fontSize，用 1.05 系数估算
  const items = dims.map((d, i) => ({
    ...d,
    color: COLORS[i % 6],
    size: Math.round(16 + (d.avg_score / maxScore) * 20),
  }))
  const charW = (sz: number) => sz * 1.05
  const gap = 20

  // 行布局：每行内按宽度排列
  const rows: { items: typeof items; totalW: number }[] = []
  let curRow: typeof items = [], curW = 0
  for (const it of items) {
    const estW = it.name.length * charW(it.size) + gap
    if (curW + estW > W - 20 && curRow.length > 0) {
      rows.push({ items: curRow, totalW: curW - gap })
      curRow = [it]; curW = estW
    } else { curRow.push(it); curW += estW }
  }
  if (curRow.length) rows.push({ items: curRow, totalW: curW - gap })

  const rowH = 46
  const H = rows.length * rowH + 16
  let s = `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">`
  rows.forEach((row, ri) => {
    let x = (W - row.totalW) / 2
    const y = ri * rowH + 34
    for (const it of row.items) {
      s += `<text x="${x.toFixed(1)}" y="${y}" font-weight="900" font-size="${it.size}" fill="${it.color}" stroke="#000" stroke-width="0.5">${it.name}</text>`
      x += it.name.length * charW(it.size) + gap
    }
  })
  s += '</svg>'
  return s
})

function retake() {
  if (record.value) router.push(`/career/test/${record.value.type}`)
}

function triggerRecommendation() {
  if (record.value) store.fetchRecommendation(record.value.id)
}

onMounted(async () => {
  const id = route.params.id as string
  const result = await store.fetchResult(id)
  record.value = result
  loading.value = false
  // 结果加载完成后自动触发 AI 岗位推荐
  if (result) triggerRecommendation()
})
</script>
