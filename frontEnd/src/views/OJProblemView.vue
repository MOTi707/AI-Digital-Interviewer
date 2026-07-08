<template>
  <div class="h-screen w-full bg-memphis-cream flex flex-col overflow-hidden">
    <!-- 顶部导航栏 -->
    <nav class="shrink-0 bg-white border-b-4 border-black px-4 py-2 flex items-center justify-between z-50">
      <div class="flex items-center gap-4">
        <button
          class="px-3 py-1.5 font-black text-xs border-4 border-black bg-white shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[1px_1px_0px_0px_rgba(0,0,0,1)] transition-all duration-200"
          @click="goBack"
        >
          ← 返回题库
        </button>
        <div v-if="problem" class="flex items-center gap-3">
          <span class="font-mono text-sm font-black">{{ problem.display_id }}</span>
          <span class="font-black text-lg">{{ problem.title }}</span>
          <span
            class="px-2 py-0.5 font-black text-xs border-2 border-black"
            :class="difficultyBg(problem.difficulty)"
          >
            {{ difficultyLabel(problem.difficulty) }}
          </span>
        </div>
      </div>
      <div v-if="problem" class="flex items-center gap-3">
        <span class="font-mono text-xs text-gray-600">通过率 {{ problem.acceptance_rate }}%</span>
        <span class="font-mono text-xs text-gray-600">提交 {{ problem.total_submissions }}</span>
      </div>
    </nav>

    <!-- 主内容区 -->
    <main class="flex-1 min-h-0 overflow-hidden px-3 py-3 grid grid-cols-12 gap-3">
      <!-- 左侧：题目信息 -->
      <div class="col-span-7 flex flex-col min-h-0 overflow-y-auto">
        <div v-if="problem" class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-4 space-y-3">
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

          <!-- 样例输入输出 -->
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

          <!-- 标签 -->
          <section>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="tag in problem.tags.split(',').filter(Boolean)"
                :key="tag"
                class="font-mono text-xs px-2 py-1 border-2 border-black bg-white hover:bg-memphis-cream transition-colors cursor-pointer"
              >
                {{ tag }}
              </span>
            </div>
          </section>
        </div>

        <div v-else class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-12 text-center">
          <div class="font-mono text-sm text-gray-600">加载中...</div>
        </div>
      </div>

      <!-- 右侧：代码编辑器 -->
      <div class="col-span-5 flex flex-col min-h-0 gap-2">
        <!-- 代码编辑器 -->
        <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-3 flex flex-col" style="flex: 1 1 0; min-height: 0;">
          <div class="flex items-center justify-between mb-2">
            <h3 class="font-black text-sm tracking-tight">💻 代码编辑</h3>
            <select
              v-model="selectedLanguage"
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
              :disabled="submitting"
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
            <h3 class="font-black text-sm tracking-tight"> 调试运行</h3>
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

        <!-- 最近提交记录 -->
        <div v-if="recentSubmissions.length > 0" class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-3 max-h-[120px] overflow-y-auto shrink-0">
          <h3 class="font-black text-sm tracking-tight mb-2">📋 提交记录</h3>
          <div class="space-y-1.5">
            <div
              v-for="sub in recentSubmissions"
              :key="sub.id"
              class="flex items-center justify-between border-2 border-black p-2 text-xs"
            >
              <span class="font-mono">{{ sub.language }}</span>
              <span
                class="font-black px-2 py-0.5 border border-black"
                :class="sub.status === 'accepted' ? 'bg-[#dcfce7] text-[#166534]' : 'bg-[#fef2f2] text-[#991b1b]'"
              >
                {{ statusLabel(sub.status) }}
              </span>
              <span class="font-mono text-gray-600">{{ sub.execution_time }}ms</span>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 判题结果弹窗 -->
    <div
      v-if="showResultModal"
      class="fixed inset-0 z-[100] flex items-center justify-center bg-black/50"
      @click.self="showResultModal = false"
    >
      <div
        class="bg-white border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] p-6 max-w-md w-full mx-4"
      >
        <div class="text-center space-y-3">
          <div class="text-5xl">{{ modalResult?.status === 'accepted' ? '🎉' : '😢' }}</div>
          <h3
            class="font-black text-xl tracking-tight"
            :class="modalResult?.status === 'accepted' ? 'text-[#166534]' : 'text-[#991b1b]'"
          >
            {{ modalResult?.status === 'accepted' ? '恭喜通过！' : '未通过' }}
          </h3>
          <div class="font-mono text-sm text-gray-700 space-y-1">
            <div v-if="modalResult?.execution_time">
              执行时间: <span class="font-black">{{ modalResult.execution_time }}ms</span>
            </div>
          </div>
          <!-- 判题状态 + 错误详情 -->
          <div
            v-if="modalResult?.status !== 'accepted'"
            class="border-2 border-black p-3 bg-[#fef2f2] text-left max-h-[200px] overflow-y-auto"
          >
            <div class="font-black text-xs text-[#991b1b] mb-1">{{ modalTitle }}</div>
            <pre v-if="modalResult?.error_detail" class="font-mono text-xs text-[#991b1b] whitespace-pre-wrap">{{ modalResult.error_detail }}</pre>
          </div>
          <button
            class="mt-2 w-full bg-memphis-coral text-white font-black py-3 border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[3px] hover:translate-y-[3px] transition-all duration-200 text-sm"
            @click="showResultModal = false"
          >
            确定
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useOjStore } from '@/stores/oj'
import type { SubmissionResult } from '@/stores/oj'

const route = useRoute()
const router = useRouter()
const ojStore = useOjStore()

const problem = computed(() => ojStore.currentProblem)
const code = ref('')
const selectedLanguage = ref('python3')
const submitting = ref(false)
const recentSubmissions = ref<SubmissionResult[]>([])

// 弹窗相关
const showResultModal = ref(false)
const modalResult = ref<SubmissionResult | null>(null)

// 首次成功代码（只保留第一次通过的代码）
const savedCode = ref('')
const savedLanguage = ref('')
const hasAccepted = ref(false)

// 调试相关
const debugging = ref(false)
const debugOutput = ref('')
const debugError = ref('')
const debugTime = ref(0)
const debugStatus = ref('')

const codePlaceholder = computed(() => {
  const placeholders: Record<string, string> = {
    python3: '# 在此输入你的 Python3 代码\n\ndef solve():\n    # 读取输入\n    n = int(input())\n    nums = list(map(int, input().split()))\n    # 编写你的代码\n    pass\n\nsolve()',
    c: '#include <stdio.h>\n\nint main() {\n    int n;\n    scanf("%d", &n);\n    int nums[10005];\n    for (int i = 0; i < n; i++) scanf("%d", &nums[i]);\n    // 编写你的代码\n    return 0;\n}',
    cpp: '#include <iostream>\n#include <vector>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    vector<int> nums(n);\n    for (int i = 0; i < n; i++) cin >> nums[i];\n    // 编写你的代码\n    return 0;\n}',
    java: 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        // 编写你的代码\n    }\n}',
    javascript: 'const readline = require("readline");\nconst rl = readline.createInterface({ input: process.stdin });\nconst lines = [];\nrl.on("line", (line) => lines.push(line));\nrl.on("close", () => {\n    // 编写你的代码\n    console.log(lines);\n});',
  }
  return placeholders[selectedLanguage.value] || ''
})

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

function difficultyBg(d: string) {
  if (d === 'easy') return 'bg-[#22c55e] text-white'
  if (d === 'medium') return 'bg-memphis-yellow'
  return 'bg-memphis-coral text-white'
}

function difficultyLabel(d: string) {
  if (d === 'easy') return '简单'
  if (d === 'medium') return '中等'
  return '困难'
}

function statusLabel(s: string) {
  const map: Record<string, string> = {
    accepted: '通过',
    wrong_answer: '答案错误',
    time_limit_exceeded: '超时',
    runtime_error: '运行时错误',
    compilation_error: '编译错误',
  }
  return map[s] || s
}

const modalTitle = computed(() => {
  if (!modalResult.value) return ''
  return statusLabel(modalResult.value.status)
})

function goBack() {
  router.push('/dashboard')
}

async function handleSubmit() {
  if (!code.value.trim()) {
    debugError.value = '请先输入代码'
    return
  }
  if (!problem.value) {
    debugError.value = '题目未加载，请稍后重试'
    return
  }
  submitting.value = true
  try {
    const result = await ojStore.submitCode(
      problem.value.id,
      code.value,
      selectedLanguage.value,
    )
    if (result.success && result.result) {
      recentSubmissions.value.unshift(result.result)
      if (recentSubmissions.value.length > 10) recentSubmissions.value.pop()

      // 保存首次通过的代码
      if (result.result.status === 'accepted' && !hasAccepted.value) {
        hasAccepted.value = true
        savedCode.value = code.value
        savedLanguage.value = selectedLanguage.value
      }

      // 弹窗显示结果
      modalResult.value = result.result
      showResultModal.value = true
    } else {
      debugError.value = result.message
    }
  } catch (e) {
    debugError.value = `提交失败: ${(e as Error).message}`
  } finally {
    submitting.value = false
  }
}

async function handleDebug() {
  if (!code.value.trim()) {
    debugError.value = '请先在代码编辑器中输入代码'
    return
  }
  if (!problem.value) {
    debugError.value = '题目未加载，请稍后重试'
    return
  }
  // 使用题目的第一组样例输入
  let sampleInput = ''
  try {
    const inputs = JSON.parse(problem.value.sample_input || '[]')
    sampleInput = inputs[0] || ''
  } catch { sampleInput = '' }

  debugging.value = true
  debugOutput.value = ''
  debugError.value = ''
  debugTime.value = 0
  debugStatus.value = ''
  try {
    const result = await ojStore.debugCode(
      problem.value.id,
      code.value,
      selectedLanguage.value,
      sampleInput,
    )
    if (result.success && result.result) {
      debugOutput.value = result.result.stdout
      debugError.value = result.result.stderr
      debugTime.value = result.result.execution_time
      debugStatus.value = result.result.status
    } else {
      debugError.value = result.message
    }
  } catch (e) {
    debugError.value = `调试失败: ${(e as Error).message}`
  } finally {
    debugging.value = false
  }
}

function copyText(text: string) {
  navigator.clipboard.writeText(text).catch(() => {})
}

onMounted(async () => {
  const problemId = route.params.id as string
  await ojStore.fetchProblem(problemId)

  // 恢复首次成功的代码
  const storageKey = `oj_saved_${problemId}`
  try {
    const saved = localStorage.getItem(storageKey)
    if (saved) {
      const data = JSON.parse(saved)
      savedCode.value = data.code || ''
      savedLanguage.value = data.language || 'python3'
      hasAccepted.value = true
      // 如果有保存的代码，默认显示
      if (savedCode.value && !code.value) {
        code.value = savedCode.value
        selectedLanguage.value = savedLanguage.value
      }
    }
  } catch {
    // ignore
  }
})

// 提交成功后保存到 localStorage
watch(hasAccepted, (val) => {
  if (val && problem.value && savedCode.value) {
    const storageKey = `oj_saved_${problem.value.id}`
    localStorage.setItem(storageKey, JSON.stringify({
      code: savedCode.value,
      language: savedLanguage.value,
    }))
  }
})
</script>
