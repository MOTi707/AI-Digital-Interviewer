<template>
  <div class="flex flex-col h-full">
    <!-- 顶部信息栏（计时器 + 轮次标题） -->
    <div class="shrink-0 flex items-center justify-between mb-2">
      <div>
        <h2 class="font-black text-xl">一面·技术面试</h2>
        <p class="font-sans text-xs text-gray-600 mt-1">完成一道编程题，限时{{ timeLimitMin }}分钟</p>
      </div>
      <div class="border-2 border-black bg-[#ff006e] text-white px-3 py-1 font-black text-sm" :class="timer <= 60 ? 'animate-pulse' : ''">
        ⏱️ {{ formatTime(timer) }}
      </div>
    </div>

    <!-- 主内容区：左题目 + 右代码编辑器（OJ风格布局） -->
    <main v-if="problem" class="flex-1 min-h-0 overflow-hidden grid grid-cols-12 gap-3">
      <!-- 左侧：题目信息 -->
      <div class="col-span-7 flex flex-col min-h-0 overflow-y-auto">
        <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-4 space-y-3">
          <!-- 题目描述 -->
          <section>
            <h3 class="font-black text-base tracking-tight mb-2 flex items-center gap-2">
              <span class="w-6 h-6 bg-memphis-coral text-white border-2 border-black flex items-center justify-center text-xs">1</span>
              题目描述
            </h3>
            <div class="font-mono text-sm text-gray-800 whitespace-pre-line leading-relaxed pl-8">
              {{ problem.description }}
            </div>
          </section>

          <!-- 输入格式 -->
          <section>
            <h3 class="font-black text-base tracking-tight mb-2 flex items-center gap-2">
              <span class="w-6 h-6 bg-memphis-yellow border-2 border-black flex items-center justify-center text-xs">2</span>
              输入格式
            </h3>
            <div class="font-mono text-sm text-gray-800 whitespace-pre-line leading-relaxed pl-8 bg-memphis-cream border-2 border-black p-3">
              {{ problem.input_format }}
            </div>
          </section>

          <!-- 输出格式 -->
          <section>
            <h3 class="font-black text-base tracking-tight mb-2 flex items-center gap-2">
              <span class="w-6 h-6 bg-memphis-blue text-white border-2 border-black flex items-center justify-center text-xs">3</span>
              输出格式
            </h3>
            <div class="font-mono text-sm text-gray-800 whitespace-pre-line leading-relaxed pl-8 bg-memphis-cream border-2 border-black p-3">
              {{ problem.output_format }}
            </div>
          </section>

          <!-- 数据范围 -->
          <section>
            <h3 class="font-black text-base tracking-tight mb-2 flex items-center gap-2">
              <span class="w-6 h-6 bg-memphis-purple text-white border-2 border-black flex items-center justify-center text-xs">4</span>
              数据范围
            </h3>
            <div class="font-mono text-sm text-gray-800 whitespace-pre-line leading-relaxed pl-8">
              {{ problem.constraints }}
            </div>
          </section>

          <!-- 样例数据 -->
          <section>
            <h3 class="font-black text-base tracking-tight mb-2 flex items-center gap-2">
              <span class="w-6 h-6 bg-memphis-orange text-white border-2 border-black flex items-center justify-center text-xs">5</span>
              样例数据
            </h3>
            <div class="pl-8 space-y-3">
              <div
                v-for="(sample, idx) in samples"
                :key="idx"
                class="border-2 border-black"
              >
                <div class="bg-memphis-cream border-b-2 border-black px-3 py-1 flex items-center justify-between">
                  <span class="font-black text-xs">样例 {{ idx + 1 }}</span>
                  <button
                    class="font-mono text-[10px] px-2 py-0.5 border border-black bg-white hover:bg-memphis-yellow transition-colors"
                    @click="copyText(sample.input + '\n' + sample.output)"
                  >
                    📋 复制
                  </button>
                </div>
                <div class="grid grid-cols-2">
                  <div class="p-3 border-r-2 border-black">
                    <div class="font-black text-[10px] mb-1 text-gray-600">输入</div>
                    <pre class="font-mono text-xs whitespace-pre-wrap">{{ sample.input }}</pre>
                  </div>
                  <div class="p-3">
                    <div class="font-black text-[10px] mb-1 text-gray-600">输出</div>
                    <pre class="font-mono text-xs whitespace-pre-wrap">{{ sample.output }}</pre>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <!-- 样例解释 -->
          <section v-if="problem.hint">
            <h3 class="font-black text-base tracking-tight mb-2 flex items-center gap-2">
              <span class="w-6 h-6 bg-[#22c55e] text-white border-2 border-black flex items-center justify-center text-xs">💡</span>
              样例解释
            </h3>
            <div class="font-mono text-sm text-gray-800 whitespace-pre-line leading-relaxed pl-8 bg-memphis-cream border-2 border-black p-3">
              {{ problem.hint }}
            </div>
          </section>

          <!-- 判题限制 -->
          <section>
            <h3 class="font-black text-base tracking-tight mb-2 flex items-center gap-2">
              <span class="w-6 h-6 bg-black text-white border-2 border-black flex items-center justify-center text-xs">⚙</span>
              判题限制
            </h3>
            <div class="pl-8 grid grid-cols-2 gap-3">
              <div class="border-2 border-black p-3 bg-white">
                <div class="font-black text-xs mb-1">⏱️ 时间限制</div>
                <div class="font-mono text-lg font-black text-memphis-coral">{{ problem.time_limit }}ms</div>
              </div>
              <div class="border-2 border-black p-3 bg-white">
                <div class="font-black text-xs mb-1">💾 内存限制</div>
                <div class="font-mono text-lg font-black text-memphis-blue">{{ problem.memory_limit }}MB</div>
              </div>
            </div>
          </section>
        </div>
      </div>

      <!-- 右侧：代码编辑器 + 调试 -->
      <div class="col-span-5 flex flex-col min-h-0 gap-2">
        <!-- 代码编辑器 -->
        <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-3 flex flex-col" style="flex: 1 1 0; min-height: 0;">
          <div class="flex items-center justify-between mb-2">
            <h3 class="font-black text-sm tracking-tight">💻 代码编辑</h3>
            <select
              v-model="language"
              class="border-2 border-black px-2 py-1 font-mono text-xs focus:outline-none focus:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all"
            >
              <option value="python3">Python3</option>
              <option value="c">C</option>
              <option value="cpp">C++</option>
              <option value="java">Java</option>
              <option value="javascript">JavaScript</option>
            </select>
          </div>

          <textarea
            v-model="code"
            class="flex-1 min-h-0 border-4 border-black font-mono text-xs p-2 resize-none focus:shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] focus:outline-none transition-all bg-memphis-cream"
            :placeholder="codePlaceholder"
            spellcheck="false"
          />

          <div class="mt-2 flex gap-2 shrink-0">
            <button
              class="flex-1 bg-[#22c55e] text-white font-black py-2 border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[3px] hover:translate-y-[3px] transition-all duration-200 text-xs"
              :disabled="submitting || !!submitResult"
              @click="handleSubmit"
            >
              {{ submitting ? '⏳ 提交中...' : '🚀 提交代码' }}
            </button>
            <button
              class="px-3 bg-white font-black py-2 border-4 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:shadow-[1px_1px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200 text-xs"
              @click="code = ''"
            >
              🗑️
            </button>
          </div>
        </div>

        <!-- 调试区域 -->
        <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-3 shrink-0">
          <div class="flex items-center justify-between mb-2">
            <h3 class="font-black text-sm tracking-tight">🧪 调试运行</h3>
            <button
              class="px-3 bg-[#8338ec] text-white font-black py-1.5 border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:shadow-[1px_1px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200 text-xs"
              :disabled="debugging"
              @click="handleDebug"
            >
              {{ debugging ? '运行中...' : '▶ 运行' }}
            </button>
          </div>
          <div v-if="debugOutput || debugError" class="border-2 border-black p-2 bg-memphis-cream min-h-[40px] max-h-[100px] overflow-auto">
            <pre v-if="debugOutput" class="font-mono text-xs whitespace-pre-wrap">{{ debugOutput }}</pre>
            <pre v-if="debugError" class="font-mono text-xs text-[#991b1b] whitespace-pre-wrap">{{ debugError }}</pre>
          </div>
          <div v-if="debugTime" class="mt-1 font-mono text-[10px] text-gray-600">
            执行时间: {{ debugTime }}ms | 状态: {{ debugStatus }}
          </div>
        </div>

        <!-- 提交结果 -->
        <div v-if="submitResult" class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-3 shrink-0"
          :class="submitResult.correct ? 'border-[#22c55e]' : 'border-red-400'">
          <div class="font-black text-sm mb-1"
            :class="submitResult.correct ? 'text-[#166534]' : 'text-[#991b1b]'">
            {{ submitResult.correct ? '✅ Accepted - 通过！' : '❌ ' + getJudgementStatus(submitResult.feedback) }}
          </div>
          <p class="font-sans text-xs text-gray-600 whitespace-pre-wrap">{{ submitResult.feedback }}</p>
        </div>
      </div>
    </main>

    <!-- 轮次完成 -->
    <div v-if="roundComplete" class="mt-4 border-4 border-black bg-white shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-6 text-center">
      <div class="text-4xl mb-3">💻</div>
      <h3 class="font-black text-xl mb-2">技术面完成！</h3>
      <p class="font-sans text-sm text-gray-600 mb-4">
        {{ submitResult?.correct ? '代码通过全部测试用例' : '代码未完全通过测试用例' }}
      </p>
      <button
        class="border-4 border-black bg-[#ff006e] text-white font-black px-6 py-2 shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all duration-200"
        @click="emit('roundComplete')"
      >
        进入下一轮 →
      </button>
    </div>

    <!-- 无题目 -->
    <div v-if="!problem && questions.length === 0" class="border-4 border-black bg-white shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-8 text-center">
      <p class="font-sans text-sm text-gray-600">暂无技术面题目</p>
      <button
        class="mt-4 border-4 border-black bg-[#ff006e] text-white font-black px-6 py-2 shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all duration-200"
        @click="emit('roundComplete')"
      >
        跳过此轮 →
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted, inject } from 'vue'
import { useInterviewStore, type QuestionItem } from '@/stores/interview'

const props = defineProps<{
  questions: QuestionItem[]
  sessionId: string
}>()

const emit = defineEmits<{
  roundComplete: []
}>()

const showAlert = inject<(msg: string, icon?: string) => void>('showAlert', (msg) => alert(msg))

const store = useInterviewStore()
const language = ref('python3')
const code = ref('')
const submitting = ref(false)
const roundComplete = ref(false)
const submitResult = ref<{ correct: boolean; feedback: string } | null>(null)
const timer = ref(900)
let timerInterval: ReturnType<typeof setInterval> | null = null
const questionStartTime = Date.now()

// 调试相关
const debugging = ref(false)
const debugOutput = ref('')
const debugError = ref('')
const debugTime = ref(0)
const debugStatus = ref('')

const problem = computed(() => {
  const q = props.questions[0]
  if (!q) return null
  return q.content as any
})

const timeLimitMin = computed(() => Math.ceil((props.questions[0]?.time_limit || 900) / 60))

// 题目ID即为OJ的problem.id，用于调试接口
const problemId = computed(() => props.questions[0]?.id || '')

const samples = computed(() => {
  if (!problem.value) return []
  try {
    const inputs = JSON.parse(problem.value.sample_input) as string[]
    const outputs = JSON.parse(problem.value.sample_output) as string[]
    return inputs.map((input, idx) => ({
      input,
      output: outputs[idx] || '',
    }))
  } catch {
    return []
  }
})

const codePlaceholder = computed(() => {
  const placeholders: Record<string, string> = {
    python3: '# 在此输入你的 Python3 代码\n\ndef solve():\n    # 读取输入\n    n = int(input())\n    nums = list(map(int, input().split()))\n    # 编写你的代码\n    pass\n\nsolve()',
    c: '#include <stdio.h>\n\nint main() {\n    int n;\n    scanf("%d", &n);\n    int nums[10005];\n    for (int i = 0; i < n; i++) scanf("%d", &nums[i]);\n    // 编写你的代码\n    return 0;\n}',
    cpp: '#include <iostream>\n#include <vector>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<int> nums(n);\n    for (int i = 0; i < n; i++) cin >> nums[i];\n    // 编写你的代码\n    return 0;\n}',
    java: 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        // 编写你的代码\n    }\n}',
    javascript: 'const readline = require("readline");\nconst rl = readline.createInterface({ input: process.stdin });\nconst lines = [];\nrl.on("line", (line) => lines.push(line));\nrl.on("close", () => {\n    // 编写你的代码\n    console.log(lines);\n});',
  }
  return placeholders[language.value] || ''
})

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}

function getJudgementStatus(feedback: string): string {
  if (feedback.includes('accepted')) return 'Accepted'
  if (feedback.includes('wrong_answer')) return 'Wrong Answer'
  if (feedback.includes('compilation_error')) return 'Compilation Error'
  if (feedback.includes('runtime_error')) return 'Runtime Error'
  if (feedback.includes('time_limit')) return 'Time Limit Exceeded'
  return feedback.split('\n')[0]
}

function copyText(text: string) {
  navigator.clipboard.writeText(text).catch(() => {})
}

function startTimer() {
  timer.value = props.questions[0]?.time_limit || 900
  if (timerInterval) clearInterval(timerInterval)
  timerInterval = setInterval(() => {
    timer.value--
    if (timer.value <= 0) {
      if (timerInterval) clearInterval(timerInterval)
      if (!submitResult.value) {
        handleSubmit()
      }
    }
  }, 1000)
}

// 调试运行（调用OJ的debug接口）
async function handleDebug() {
  if (!code.value.trim()) {
    debugError.value = '请先在代码编辑器中输入代码'
    return
  }
  if (!problemId.value) {
    debugError.value = '题目未加载，请稍后重试'
    return
  }
  // 使用第一组样例输入
  let sampleInput = ''
  try {
    const inputs = JSON.parse(problem.value?.sample_input || '[]')
    sampleInput = inputs[0] || ''
  } catch { sampleInput = '' }

  debugging.value = true
  debugOutput.value = ''
  debugError.value = ''
  debugTime.value = 0
  debugStatus.value = ''
  try {
    const token = localStorage.getItem('auth_token')
    const res = await fetch(`/api/problems/${problemId.value}/debug`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ code: code.value, language: language.value, input_data: sampleInput }),
    })
    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      throw new Error(body.detail || `调试失败 (${res.status})`)
    }
    const result = await res.json()
    debugOutput.value = result.stdout || ''
    debugError.value = result.stderr || ''
    debugTime.value = result.execution_time || 0
    debugStatus.value = result.status || ''
  } catch (e) {
    debugError.value = `调试失败: ${(e as Error).message}`
  } finally {
    debugging.value = false
  }
}

async function handleSubmit() {
  if (submitting.value || submitResult.value) return
  if (!code.value.trim()) {
    showAlert('请输入代码后再提交哦', '💻')
    return
  }

  submitting.value = true
  const duration = Math.floor((Date.now() - questionStartTime) / 1000)

  try {
    const result = await store.submitAnswer(
      props.sessionId,
      props.questions[0].id,
      { code: code.value, language: language.value },
      duration
    )
    submitResult.value = { correct: result.correct, feedback: result.feedback }
    if (timerInterval) clearInterval(timerInterval)
    setTimeout(() => {
      roundComplete.value = true
    }, 2000)
  } catch (e) {
    showAlert(`提交失败: ${(e as Error).message}`, '❌')
  } finally {
    submitting.value = false
  }
}

watch(() => props.questions, (newQ) => {
  if (newQ.length > 0) {
    roundComplete.value = false
    submitResult.value = null
    code.value = ''
    debugOutput.value = ''
    debugError.value = ''
    debugTime.value = 0
    debugStatus.value = ''
    startTimer()
  }
}, { immediate: true })

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
})
</script>
