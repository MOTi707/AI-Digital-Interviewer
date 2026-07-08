<template>
  <div class="h-screen w-screen flex flex-col overflow-hidden bg-memphis-cream">
    <!-- 顶部导航栏 -->
    <nav class="shrink-0 bg-white border-b-4 border-black px-6 py-1.5 flex items-center justify-between z-50">
      <div class="flex items-center gap-4">
        <router-link
          to="/resume"
          class="flex items-center gap-2 px-3 py-1.5 border-4 border-black bg-white font-black text-sm hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200"
        >
          ← 返回简历分析
        </router-link>
        <div class="flex items-center gap-2">
          <div class="w-7 h-7 bg-memphis-orange border-2 border-black flex items-center justify-center">
            <span class="text-sm">✨</span>
          </div>
          <span class="font-black text-xl tracking-tight">简历措辞优化</span>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <span v-if="!resumeStore.hasApiKey" class="font-mono text-sm px-3 py-1 border-2 border-black bg-memphis-coral text-white">
          ⚠ 后端未配置 API Key
        </span>
        <button
          v-if="!resumeStore.optimizing"
          class="px-4 py-1.5 border-4 border-black bg-memphis-orange text-white font-black text-sm shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200"
          :disabled="!resumeStore.hasResume || !resumeStore.hasApiKey"
          @click="runOptimize"
        >
          🔄 AI 一键优化
        </button>
        <button v-else class="px-4 py-1.5 border-4 border-black bg-black text-white font-black text-sm" disabled>
          ⏳ 优化中...
        </button>
      </div>
    </nav>

    <!-- 主内容区 -->
    <main class="flex-1 overflow-hidden p-4 flex flex-col gap-4">
      <!-- 操作说明 -->
      <div class="shrink-0 bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-3 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <span class="w-8 h-8 bg-memphis-orange border-2 border-black flex items-center justify-center text-base">💡</span>
          <div>
            <div class="font-black text-sm">AI 智能措辞优化</div>
            <div class="font-mono text-xs text-gray-600">左侧为原文，右侧为 AI 优化后的版本，红色为删除内容，绿色为优化内容</div>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span class="font-mono text-xs px-2 py-1 border-2 border-black bg-memphis-yellow">共 {{ diffOriginal.length }} 条优化</span>
          <span class="font-mono text-xs px-2 py-1 border-2 border-black bg-memphis-coral text-white">Deepseek AI</span>
        </div>
      </div>

      <!-- Diff 对比区 -->
      <div class="flex-1 grid grid-cols-[2fr_3fr] gap-4 min-h-0">
        <!-- 原文 -->
        <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] flex flex-col overflow-hidden">
          <div class="shrink-0 px-4 py-2.5 border-b-4 border-black bg-memphis-cream flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="text-base">📝</span>
              <span class="font-black text-sm">原文</span>
            </div>
            <span class="font-mono text-xs px-2 py-0.5 border-2 border-black bg-white">修改前</span>
          </div>
          <div class="flex-1 overflow-y-auto p-4 font-mono text-lg leading-relaxed space-y-3">
            <template v-if="diffOriginal.length">
              <div
                v-for="(line, idx) in diffOriginal"
                :key="idx"
                class="border-2 border-black p-4"
                :class="line.type === 'removed' ? 'bg-red-50 border-red-300' : 'bg-white'"
              >
                <div class="flex items-start gap-3">
                  <span class="shrink-0 w-7 h-7 border-2 border-black flex items-center justify-center font-black text-sm" :class="line.type === 'removed' ? 'bg-memphis-coral text-white' : 'bg-white'">
                    {{ idx + 1 }}
                  </span>
                  <span class="text-lg" :class="line.type === 'removed' ? 'line-through text-red-700' : ''">{{ line.text }}</span>
                </div>
              </div>
            </template>
            <div v-else class="flex flex-col items-center justify-center h-full text-center">
              <div class="text-3xl mb-2">📝</div>
              <div class="font-black text-base mb-1">等待优化</div>
              <div class="font-mono text-xs text-gray-600">点击右上角「AI 一键优化」开始</div>
            </div>
          </div>
        </div>

        <!-- 优化后 -->
        <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] flex flex-col overflow-hidden">
          <div class="shrink-0 px-4 py-2.5 border-b-4 border-black bg-memphis-cream flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="text-base">✨</span>
              <span class="font-black text-sm">优化后</span>
            </div>
            <span class="font-mono text-xs px-2 py-0.5 border-2 border-black bg-white">AI 优化版</span>
          </div>
          <div class="flex-1 overflow-y-auto p-4 font-mono text-lg leading-relaxed space-y-3">
            <template v-if="diffOptimized.length">
              <div
                v-for="(line, idx) in diffOptimized"
                :key="idx"
                class="border-2 border-black p-4"
                :class="line.type === 'added' ? 'bg-green-50 border-green-300' : 'bg-white'"
              >
                <div class="flex items-start gap-3">
                  <span class="shrink-0 w-7 h-7 border-2 border-black flex items-center justify-center font-black text-sm" :class="line.type === 'added' ? 'bg-[#22c55e] text-white' : 'bg-white'">
                    {{ idx + 1 }}
                  </span>
                  <span class="text-lg" :class="line.type === 'added' ? 'font-bold text-green-800' : ''">{{ line.text }}</span>
                </div>
              </div>
            </template>
            <div v-else class="flex flex-col items-center justify-center h-full text-center">
              <div class="text-3xl mb-2">✨</div>
              <div class="font-black text-base mb-1">等待优化</div>
              <div class="font-mono text-xs text-gray-600">AI 优化结果将显示在这里</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 优化统计 -->
      <div class="shrink-0 grid grid-cols-4 gap-3">
        <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-3 text-center">
          <div class="font-black text-3xl text-memphis-coral">{{ stats.total_optimized || diffOriginal.length || 0 }}</div>
          <div class="font-mono text-xs text-gray-700 mt-0.5">优化条数</div>
        </div>
        <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-3 text-center">
          <div class="font-black text-3xl text-[#22c55e]">{{ stats.professionalism_improvement || '-' }}</div>
          <div class="font-mono text-xs text-gray-700 mt-0.5">专业度提升</div>
        </div>
        <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-3 text-center">
          <div class="font-black text-3xl text-memphis-purple">+{{ stats.quantified_metrics_added || 0 }}</div>
          <div class="font-mono text-xs text-gray-700 mt-0.5">新增量化指标</div>
        </div>
        <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-3 text-center">
          <div class="font-black text-3xl text-memphis-yellow">{{ stats.overall_rating || '-' }}</div>
          <div class="font-mono text-xs text-gray-700 mt-0.5">综合评级</div>
        </div>
      </div>
    </main>

    <!-- Loading 弹窗 -->
    <div
      v-if="showLoadingModal"
      class="fixed inset-0 z-[9999] flex items-center justify-center bg-black/60"
    >
      <div class="border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] bg-[#fef9ef] p-8 md:p-12 flex flex-col items-center gap-6 min-w-[280px]">
        <!-- 弹跳圆点动画 -->
        <div class="flex items-center gap-3">
          <span class="loading-dot w-4 h-4 bg-memphis-coral border-2 border-black"></span>
          <span class="loading-dot w-4 h-4 bg-memphis-orange border-2 border-black" style="animation-delay: 0.15s"></span>
          <span class="loading-dot w-4 h-4 bg-memphis-yellow border-2 border-black" style="animation-delay: 0.3s"></span>
        </div>
        <!-- 动态文字 -->
        <Transition name="slide-up" mode="out-in">
          <div class="font-black text-2xl md:text-3xl tracking-tight text-center" :key="loadingText">{{ loadingText }}</div>
        </Transition>
        <!-- 提示 -->
        <div class="font-mono text-xs text-gray-700">请稍候，AI 正在处理...</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useResumeStore } from '@/stores/resume'

const resumeStore = useResumeStore()

const diffOriginal = ref<{ text: string; type: string }[]>([])
const diffOptimized = ref<{ text: string; type: string }[]>([])
const stats = ref<Record<string, unknown>>({})

// ── Loading 弹窗状态 ──
const showLoadingModal = ref(false)
const loadingText = ref('正在分析')

let loadingTimer: ReturnType<typeof setTimeout> | null = null

function startLoadingRotation() {
  // 非循环：3 个阶段，每个文字只显示 1 次，总时长约 6~9s
  const sequence = [
    { text: '正在分析', duration: 2000 + Math.random() * 1000 },
    { text: '正在优化', duration: 2000 + Math.random() * 1000 },
    { text: '正在打磨', duration: 2000 + Math.random() * 1000 },
  ]
  let idx = 0
  loadingText.value = sequence[0].text
  function next() {
    idx++
    if (idx >= sequence.length) return
    loadingText.value = sequence[idx].text
    loadingTimer = setTimeout(next, sequence[idx].duration)
  }
  loadingTimer = setTimeout(next, sequence[0].duration)
}

function stopLoadingRotation() {
  if (loadingTimer !== null) {
    clearTimeout(loadingTimer)
    loadingTimer = null
  }
  showLoadingModal.value = false
}

onBeforeUnmount(() => {
  if (loadingTimer !== null) clearTimeout(loadingTimer)
})

// ── 预加载：页面进入就发起请求，结果缓存 ──
const preloadedOriginal = ref<{ text: string; type: string }[]>([])
const preloadedOptimized = ref<{ text: string; type: string }[]>([])
const preloadedStats = ref<Record<string, unknown>>({})
const preloadDone = ref(false)
const preloadError = ref<string | null>(null)
let preloadPromise: Promise<void> | null = null

async function preloadOptimize() {
  preloadPromise = (async () => {
    try {
      await resumeStore.optimizeTextStream(
        (_idx, original, optimized) => {
          preloadedOriginal.value.push({ text: original, type: 'removed' })
          preloadedOptimized.value.push({ text: optimized, type: 'added' })
        },
        (finalStats) => {
          preloadedStats.value = finalStats
        },
        () => {},
        true, // silent: 不触发 optimizing 状态，按钮不受影响
      )
      preloadDone.value = true
    } catch (err) {
      preloadError.value = (err as Error).message
    }
  })()
}

onMounted(async () => {
  await Promise.all([resumeStore.fetchResume(), resumeStore.fetchConfig()])
  // 有简历且有 API Key 时，立即在后台发起优化请求
  if (resumeStore.resume?.raw_text && resumeStore.hasApiKey) {
    preloadOptimize()
  }
})

async function runOptimize() {
  if (!resumeStore.resume?.raw_text) {
    alert('暂无简历内容可优化')
    return
  }

  // 如果预加载已出错
  if (preloadError.value) {
    alert(`优化失败: ${preloadError.value}`)
    return
  }

  // 始终显示 Loading 弹窗，至少展示 2 秒
  showLoadingModal.value = true
  startLoadingRotation()

  const minDelay = new Promise<void>(resolve => setTimeout(resolve, 2000))

  try {
    await Promise.all([minDelay, preloadPromise])

    if (preloadError.value) {
      alert(`优化失败: ${preloadError.value}`)
    } else {
      diffOriginal.value = [...preloadedOriginal.value]
      diffOptimized.value = [...preloadedOptimized.value]
      stats.value = { ...preloadedStats.value }
    }
  } finally {
    stopLoadingRotation()
  }
}
</script>

<style scoped>
.loading-dot {
  animation: bounce-dot 0.6s ease-in-out infinite alternate;
}

@keyframes bounce-dot {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-12px);
  }
}

/* 离开：向上滑出 + 淡出 */
.slide-up-leave-active {
  transition: all 0.3s ease-in;
}
.slide-up-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}

/* 进入：从下方滑入 + 淡入 */
.slide-up-enter-active {
  transition: all 0.3s ease-out;
}
.slide-up-enter-from {
  transform: translateY(20px);
  opacity: 0;
}
</style>
