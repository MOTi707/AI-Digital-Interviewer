<template>
  <div>
    <!-- 测评标题 -->
    <div class="mb-4 flex items-center justify-between">
      <div>
        <h2 class="font-black text-xl">综合素质测评</h2>
        <p class="font-sans text-xs text-gray-600 mt-1">共{{ questions.length }}道选择题，每题30秒</p>
      </div>
      <div class="border-2 border-black bg-[#3a86ff] text-white px-3 py-1 font-black text-xs">
        第 {{ currentIndex + 1 }} / {{ questions.length }} 题
      </div>
    </div>

    <!-- 进度条 -->
    <div class="border-2 border-black bg-white mb-4 h-3">
      <div
        class="h-full bg-[#3a86ff] transition-all duration-300"
        :style="{ width: `${((currentIndex) / questions.length) * 100}%` }"
      />
    </div>

    <!-- 当前题目 -->
    <div v-if="currentQuestion" class="border-4 border-black bg-white shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-6">
      <!-- 倒计时 -->
      <div class="flex items-center justify-between mb-4">
        <div class="font-black text-sm" :class="timer <= 10 ? 'text-red-600' : 'text-black'">
          ⏱️ 剩余 {{ timer }}s
        </div>
        <div class="border-2 border-black px-2 py-0.5 text-xs font-black bg-[#fef9ef]">
          选择题
        </div>
      </div>

      <!-- 题目文本 -->
      <p class="font-sans mb-6 leading-relaxed" :style="{ fontSize: qFontSize }">{{ (currentQuestion.content as any).text }}</p>

      <!-- 选项 -->
      <div class="space-y-3">
        <button
          v-for="(option, idx) in (currentQuestion.content as any).options"
          :key="idx"
          :disabled="answered"
          :class="[
            'w-full text-left border-4 border-black px-4 py-3 font-sans transition-all duration-200',
            selectedOption === optionLetter(idx) ? 'bg-[#3a86ff] text-white' :
            answered ? 'bg-gray-100 text-gray-500' :
            'bg-white hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px]'
          ]"
          :style="{ fontSize: optFontSize }"
          @click="selectOption(optionLetter(idx))"
        >
          <span class="font-black mr-2">{{ optionLetter(idx) }}.</span>
          {{ option }}
        </button>
      </div>
    </div>

    <!-- 轮次完成：显示全部答案 -->
    <div v-if="roundComplete" class="mt-4 border-4 border-black bg-white shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-6">
      <div class="text-center mb-4">
        <div class="text-4xl mb-3">📝</div>
        <h3 class="font-black text-xl mb-2">测评完成！</h3>
        <p class="font-sans text-sm text-gray-600">得分：{{ totalScore }} / {{ questions.length * 10 }}</p>
      </div>

      <!-- 每题结果 -->
      <div class="space-y-3 max-h-[50vh] overflow-y-auto mb-4">
        <div v-for="(item, idx) in answerHistory" :key="idx"
          class="border-2 border-black p-3"
          :class="item.correct ? 'bg-[#22c55e]/10' : 'bg-red-50'">
          <div class="flex items-start justify-between gap-2 mb-1">
            <span class="font-black text-sm">第{{ idx + 1 }}题</span>
            <span class="font-black text-xs px-2 py-0.5 border-2 border-black"
              :class="item.correct ? 'bg-[#22c55e] text-white' : 'bg-[#ff006e] text-white'">
              {{ item.correct ? '✅ 正确' : '❌ 错误' }}
            </span>
          </div>
          <p class="font-sans text-xs text-gray-700 mb-1">{{ item.questionText }}</p>
          <p class="font-sans text-xs">
            <span class="font-black">你的答案：</span>{{ item.userAnswer || '未作答' }}
            <span v-if="!item.correct" class="ml-2 font-black text-[#22c55e]">正确答案：{{ item.correctAnswer }}</span>
          </p>
          <p class="font-sans text-xs text-gray-600 mt-1">{{ item.feedback }}</p>
        </div>
      </div>

      <button
        class="w-full border-4 border-black bg-[#ff006e] text-white font-black px-6 py-2 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all duration-200"
        @click="emit('roundComplete')"
      >
        进入下一轮 →
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted, inject, type Ref } from 'vue'
import { useInterviewStore, type QuestionItem } from '@/stores/interview'

const props = defineProps<{
  questions: QuestionItem[]
  sessionId: string
}>()

const emit = defineEmits<{
  roundComplete: []
}>()

const fontSize = inject<Ref<number>>('fontSize', ref(16))
const qFontSize = computed(() => `${fontSize.value}px`)
const optFontSize = computed(() => `${Math.max(fontSize.value - 2, 12)}px`)

const store = useInterviewStore()
const currentIndex = ref(0)
const selectedOption = ref('')
const answered = ref(false)
const totalScore = ref(0)
const roundComplete = ref(false)
const timer = ref(30)
let timerInterval: ReturnType<typeof setInterval> | null = null
let questionStartTime = Date.now()

interface AnswerRecord {
  questionText: string
  userAnswer: string
  correctAnswer: string
  correct: boolean
  feedback: string
  score: number
}
const answerHistory = ref<AnswerRecord[]>([])

const currentQuestion = computed(() => props.questions[currentIndex.value] || null)

function optionLetter(idx: number): string {
  return String.fromCharCode(65 + idx)
}

function startTimer() {
  timer.value = 30
  if (timerInterval) clearInterval(timerInterval)
  timerInterval = setInterval(() => {
    timer.value--
    if (timer.value <= 0) {
      if (!answered.value) {
        submitCurrentAnswer('')
      }
    }
  }, 1000)
}

async function selectOption(option: string) {
  if (answered.value) return
  selectedOption.value = option
  await submitCurrentAnswer(option)
}

async function submitCurrentAnswer(answer: string) {
  answered.value = true
  if (timerInterval) clearInterval(timerInterval)

  const duration = Math.floor((Date.now() - questionStartTime) / 1000)
  try {
    const result = await store.submitAnswer(
      props.sessionId,
      currentQuestion.value!.id,
      answer,
      duration
    )
    totalScore.value += result.score

    const qContent = currentQuestion.value!.content as any
    answerHistory.value.push({
      questionText: qContent.text,
      userAnswer: answer || '未作答',
      correctAnswer: result.correct_answer as string || '',
      correct: result.correct,
      feedback: result.feedback,
      score: result.score,
    })
  } catch (e) {
    answerHistory.value.push({
      questionText: (currentQuestion.value!.content as any).text,
      userAnswer: answer || '提交失败',
      correctAnswer: '',
      correct: false,
      feedback: `提交失败: ${(e as Error).message}`,
      score: 0,
    })
  }

  setTimeout(() => {
    nextQuestion()
  }, 800)
}

function nextQuestion() {
  if (currentIndex.value < props.questions.length - 1) {
    currentIndex.value++
    selectedOption.value = ''
    answered.value = false
    questionStartTime = Date.now()
    startTimer()
  } else {
    roundComplete.value = true
  }
}

watch(() => props.questions, (newQ) => {
  if (newQ.length > 0) {
    currentIndex.value = 0
    selectedOption.value = ''
    answered.value = false
    totalScore.value = 0
    roundComplete.value = false
    answerHistory.value = []
    questionStartTime = Date.now()
    startTimer()
  }
}, { immediate: true })

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
})
</script>
