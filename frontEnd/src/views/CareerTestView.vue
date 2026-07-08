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

    <!-- 加载中 -->
    <div v-if="store.loading && !questions" class="flex items-center justify-center py-32">
      <div class="font-black text-2xl text-memphis-purple">加载中...</div>
    </div>

    <!-- 错误 -->
    <div v-else-if="store.error && !questions" class="flex items-center justify-center py-32">
      <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-8 max-w-md text-center">
        <div class="font-black text-xl text-memphis-coral mb-3">出错了</div>
        <div class="font-mono text-sm">{{ store.error }}</div>
      </div>
    </div>

    <!-- 答题主体 -->
    <div v-else-if="questions" class="max-w-2xl mx-auto px-4 py-8">

      <!-- 进度条 -->
      <div class="mb-6">
        <div class="flex justify-between mb-2">
          <span class="font-black text-sm">{{ questions.title }}</span>
          <span class="font-mono text-sm font-black">第 {{ currentIndex + 1 }} 题 · 已答 {{ answeredCount }} / {{ totalQuestions }}</span>
        </div>
        <div class="h-4 border-4 border-black bg-white">
          <div
            class="h-full bg-memphis-yellow transition-all duration-300"
            :style="{ width: progressPercent + '%' }"
          />
        </div>
      </div>

      <!-- 返回上一题按钮（左侧对齐） -->
      <div class="flex items-center justify-start mb-4" style="min-height: 48px">
        <button
          v-if="currentIndex > 0"
          class="flex items-center gap-2 px-4 py-2 border-4 border-black bg-white font-black text-sm shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] active:translate-x-[4px] active:translate-y-[4px] active:shadow-none transition-all duration-150"
          @click="goBack"
        >
          <!-- SVG 左箭头 -->
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none"
               stroke="currentColor" stroke-width="3" stroke-linecap="square" stroke-linejoin="miter">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
          上一题
        </button>
      </div>

      <!-- 题目卡片 -->
      <div
        :key="currentIndex"
        class="bg-white p-6 md:p-8 mb-6 animate-slide-in"
      >
        <!-- 题号标签 -->
        <div class="flex items-center gap-3 mb-5">
          <div class="w-10 h-10 bg-memphis-purple border-4 border-black flex items-center justify-center font-black text-sm text-white shrink-0">
            {{ currentIndex + 1 }}
          </div>
          <div class="font-black text-base md:text-lg leading-snug">{{ currentQuestion?.text }}</div>
        </div>

        <!-- 5级量表选项按钮 - 垂直排列 -->
        <div class="space-y-5">
          <button
            v-for="opt in currentQuestion?.options"
            :key="opt.value"
            :class="[
              'w-full py-3.5 px-4 border-2 border-black font-black text-sm text-left transition-all duration-150 flex items-center gap-3',
              isCurrentAnswered(opt.value)
                ? 'bg-green-500 text-white border-green-600 shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] scale-[0.98]'
                : 'bg-white shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[1px] hover:translate-y-[1px]'
            ]"
            @click="selectAnswer(opt.value)"
          >
            <!-- 选项圆形标记 -->
            <span
              :class="[
                'w-6 h-6 flex items-center justify-center font-black text-xs shrink-0',
                isCurrentAnswered(opt.value) ? 'bg-white/20 text-white' : 'bg-gray-100 text-black'
              ]"
            >
              {{ opt.value }}
            </span>
            {{ opt.label }}
          </button>
        </div>
      </div>

      <!-- 底部：导航 + 提交按钮 -->
      <div class="mb-8 flex flex-col gap-3">

        <!-- 提交按钮：全部答完时始终显示 -->
        <button
          v-if="allAnswered"
          :disabled="submitting"
          :class="[
            'w-full py-4 border-4 border-black font-black text-lg transition-all duration-200',
            !submitting
              ? 'bg-memphis-coral text-white shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[3px] hover:translate-y-[3px]'
              : 'bg-gray-200 text-gray-500 cursor-not-allowed'
          ]"
          @click="handleSubmit"
        >
          {{ submitting ? '提交中...' : '提交并查看结果 →' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCareerStore } from '@/stores/career'

const route = useRoute()
const router = useRouter()
const store = useCareerStore()

const assessmentType = computed(() => route.params.type as string)
const questions = computed(() => store.currentQuestions)
const answers = reactive<Record<string, number>>({})
const submitting = ref(false)
const currentIndex = ref(0)
let autoAdvanceTimer: ReturnType<typeof setTimeout> | null = null
let isAdvancing = false

const totalQuestions = computed(() => questions.value?.questions.length ?? 0)
const answeredCount = computed(() => Object.keys(answers).length)
const allAnswered = computed(() =>
  questions.value ? answeredCount.value === totalQuestions.value : false
)
const progressPercent = computed(() =>
  questions.value ? Math.round((answeredCount.value / totalQuestions.value) * 100) : 0
)
const currentQuestion = computed(() =>
  questions.value?.questions[currentIndex.value] ?? null
)

function isCurrentAnswered(value: number): boolean {
  const q = currentQuestion.value
  return q ? answers[q.id] === value : false
}

function selectAnswer(value: number) {
  const q = currentQuestion.value
  if (!q) return
  answers[q.id] = value
  // 自动跳转到下一题（延迟让用户看到选中反馈）
  if (currentIndex.value < totalQuestions.value - 1) {
    // 清除之前的定时器，防止快速点击导致多次跳转
    if (autoAdvanceTimer !== null) {
      clearTimeout(autoAdvanceTimer)
      autoAdvanceTimer = null
    }
    autoAdvanceTimer = setTimeout(() => {
      if (isAdvancing) return
      isAdvancing = true
      currentIndex.value++
      autoAdvanceTimer = null
      setTimeout(() => { isAdvancing = false }, 50)
    }, 280)
  }
}

function goBack() {
  if (autoAdvanceTimer !== null) {
    clearTimeout(autoAdvanceTimer)
    autoAdvanceTimer = null
  }
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}


async function handleSubmit() {
  if (!allAnswered.value) return
  submitting.value = true
  const answerList = Object.entries(answers).map(([question_id, score]) => ({
    question_id,
    score,
  }))
  const record = await store.submitAssessment(assessmentType.value, answerList)
  submitting.value = false
  if (record) {
    router.push(`/career/result/${record.id}`)
  }
}

onMounted(async () => {
  await store.fetchQuestions(assessmentType.value)
})
</script>

<style scoped>
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(16px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.animate-slide-in {
  animation: slideIn 0.2s ease-out;
}
</style>
