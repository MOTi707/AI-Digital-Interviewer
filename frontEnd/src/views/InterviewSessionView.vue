<template>
  <div class="h-screen w-screen flex flex-col bg-[#fef9ef] overflow-hidden">
    <!-- 顶部状态栏（仅面试进行中显示） -->
    <header v-if="store.currentSession?.status === 'in_progress'" class="shrink-0 bg-white border-b-4 border-black px-4 py-2">
      <div class="flex items-center justify-between mb-2">
        <div class="flex items-center gap-3">
          <span class="font-black text-sm">{{ store.currentSession?.job_title }}</span>
          <span class="text-xs font-sans text-gray-600">{{ store.currentSession?.job_category }}</span>
        </div>
        <div class="flex items-center gap-3">
          <!-- 字体大小调节（仅选择题轮次显示） -->
          <div v-if="isChoiceRound" class="flex items-center gap-1 border-2 border-black">
            <button class="px-2 py-1 font-black text-xs hover:bg-[#fef9ef] transition-colors" @click="decreaseFont">A-</button>
            <span class="px-1 font-mono text-[10px]">{{ fontSize }}px</span>
            <button class="px-2 py-1 font-black text-xs hover:bg-[#fef9ef] transition-colors" @click="increaseFont">A+</button>
          </div>
          <span v-if="cheatCount > 0" class="text-xs font-black text-red-600">
            ⚠️ 切屏 {{ cheatCount }}/5
          </span>
          <button
            class="border-2 border-black bg-[#fef9ef] px-3 py-1 font-black text-xs hover:bg-red-100 transition-colors"
            @click="handleAbort"
          >
            中止面试
          </button>
        </div>
      </div>
    </header>

    <!-- 入场须知弹窗 -->
    <Teleport to="body">
      <Transition name="modal-fade">
      <div v-if="showRules" class="fixed inset-0 bg-black/80 z-[300] flex items-center justify-center">
        <div class="border-4 border-black bg-[#fef9ef] shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] p-8 max-w-lg w-full mx-4">
          <div class="text-center mb-6">
            <div class="text-5xl mb-3">🎤</div>
            <h2 class="font-black text-2xl">面试入场须知</h2>
          </div>

          <!-- 单轮模式提示 -->
          <div v-if="isSingleMode" class="flex items-start gap-3 border-2 border-black bg-[#3a86ff]/10 p-3 border-[#3a86ff]">
            <span class="text-xl shrink-0">🎯</span>
            <div>
              <div class="font-black text-sm text-[#3a86ff]">单轮练习模式</div>
              <div class="font-sans text-xs text-gray-600">本次仅练习「{{ targetRoundLabel }}」轮，完成后将生成该轮单独报告</div>
            </div>
          </div>

          <div class="space-y-3 mb-6">
            <div v-if="ENABLE_FULLSCREEN_PROTECTION" class="flex items-start gap-3 border-2 border-black bg-white p-3">
              <span class="text-xl shrink-0">🖥️</span>
              <div>
                <div class="font-black text-sm">全屏模式</div>
                <div class="font-sans text-xs text-gray-600">面试将在全屏模式下进行，无法最小化或切换到其他窗口</div>
              </div>
            </div>
            <div class="flex items-start gap-3 border-2 border-black bg-white p-3">
              <span class="text-xl shrink-0">🚫</span>
              <div>
                <div class="font-black text-sm">禁止切屏</div>
                <div class="font-sans text-xs text-gray-600">切换标签页、打开新窗口或离开浏览器将被记录为作弊行为</div>
              </div>
            </div>
            <div class="flex items-start gap-3 border-2 border-black bg-red-50 p-3 border-red-400">
              <span class="text-xl shrink-0">⚠️</span>
              <div>
                <div class="font-black text-sm text-red-600">切屏≥5次自动中止</div>
                <div class="font-sans text-xs text-gray-600">切屏次数达到5次将自动中止面试，仅保留已答部分评分</div>
              </div>
            </div>
            <div class="flex items-start gap-3 border-2 border-black bg-white p-3">
              <span class="text-xl shrink-0">⏱️</span>
              <div>
                <div class="font-black text-sm">面试时长</div>
                <div class="font-sans text-xs text-gray-600">{{ isSingleMode ? '单轮练习约10-15分钟，每题有倒计时限制' : '全程约30-60分钟，包含5个环节，每题有倒计时限制' }}</div>
              </div>
            </div>
            <div class="flex items-start gap-3 border-2 border-black bg-white p-3">
              <span class="text-xl shrink-0">🔇</span>
              <div>
                <div class="font-black text-sm">环境要求</div>
                <div class="font-sans text-xs text-gray-600">请确保网络稳定、环境安静，提前检查麦克风和扬声器</div>
              </div>
            </div>
          </div>

          <div class="flex gap-3">
            <button
              class="flex-1 border-4 border-black bg-[#ff006e] text-white font-black py-3 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all duration-200"
              @click="acceptRules"
            >
              我已了解，开始面试
            </button>
            <button
              class="flex-1 border-4 border-black bg-white font-black py-3 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all duration-200"
              @click="handleAbort"
            >
              退出面试
            </button>
          </div>
        </div>
      </div>
      </Transition>
    </Teleport>

    <!-- 警告横幅 -->
    <Teleport to="body">
      <div
        v-if="warningMsg"
        class="fixed top-4 left-1/2 -translate-x-1/2 z-[200] border-4 border-black bg-[#ffbe0b] shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] px-6 py-3 font-black text-sm animate-bounce"
      >
        {{ warningMsg }}
      </div>
    </Teleport>

    <!-- 自定义确认弹窗 -->
    <Teleport to="body">
      <Transition name="modal-fade">
      <div v-if="confirmModal.show" class="fixed inset-0 bg-black/70 z-[250] flex items-center justify-center">
        <div class="border-4 border-black bg-[#fef9ef] shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] p-8 max-w-sm w-full mx-4">
          <div class="text-center mb-4">
            <div class="text-4xl mb-2">⚠️</div>
            <h3 class="font-black text-xl">{{ confirmModal.title }}</h3>
          </div>
          <p class="font-sans text-sm text-gray-600 text-center mb-6">{{ confirmModal.message }}</p>
          <div class="flex gap-3">
            <button
              class="flex-1 border-4 border-black bg-[#ff006e] text-white font-black py-2 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all duration-200"
              @click="confirmModal.onConfirm"
            >
              {{ confirmModal.confirmText }}
            </button>
            <button
              class="flex-1 border-4 border-black bg-white font-black py-2 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all duration-200"
              @click="confirmModal.show = false"
            >
              {{ confirmModal.cancelText }}
            </button>
          </div>
        </div>
      </div>
      </Transition>
    </Teleport>

    <!-- 提示弹窗（替代 alert） -->
    <Teleport to="body">
      <Transition name="modal-fade">
      <div v-if="alertModal.show" class="fixed inset-0 bg-black/60 z-[250] flex items-center justify-center" @click.self="alertModal.show = false">
        <div class="border-4 border-black bg-[#fef9ef] shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] p-6 max-w-xs w-full mx-4">
          <div class="text-center mb-4">
            <div class="text-3xl mb-2">{{ alertModal.icon }}</div>
            <p class="font-sans text-sm">{{ alertModal.message }}</p>
          </div>
          <button
            class="w-full border-4 border-black bg-black text-white font-black py-2 shadow-[3px_3px_0px_0px_rgba(255,0,110,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(255,0,110,1)] transition-all duration-200"
            @click="alertModal.show = false"
          >
            知道了
          </button>
        </div>
      </div>
      </Transition>
    </Teleport>

    <!-- 摄像头悬浮窗 -->
    <Teleport to="body">
      <div
        v-show="cameraStream && !cameraPipHidden"
        ref="cameraPipRef"
        class="fixed z-[150] border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] bg-black"
        :style="cameraPipStyle"
      >
        <!-- 拖动把手 -->
        <div
          class="flex items-center justify-between bg-black px-2 py-1 cursor-move select-none"
          @mousedown="startDragPip"
        >
          <span class="text-white text-xs font-black">📷 录制中</span>
          <button
            class="text-white text-xs font-black hover:text-[#ff006e] transition-colors ml-2"
            @click.stop="cameraPipHidden = true"
            title="隐藏摄像头"
          >隐藏</button>
        </div>
        <video ref="cameraVideoRef" autoplay muted playsinline class="w-full h-full object-cover" style="width: 200px; height: 150px;"></video>
      </div>
      <!-- 隐藏后的恢复按钮 -->
      <button
        v-if="cameraStream && cameraPipHidden"
        class="fixed bottom-5 right-5 z-[150] border-2 border-black bg-black text-white text-xs font-black px-2 py-1 shadow-[3px_3px_0px_0px_rgba(255,0,110,1)] hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-[2px_2px_0px_0px_rgba(255,0,110,1)] transition-all"
        @click="cameraPipHidden = false"
      >📷</button>
    </Teleport>

    <!-- 主内容区域 -->
    <main :class="['flex-1 min-h-0', (currentRound === 'tech' || currentRound === 'ai_voice_3' || currentRound === 'ai_voice_4') ? 'overflow-hidden p-4 md:p-6' : 'overflow-y-auto p-4 md:p-6']">
      <div :class="(currentRound === 'tech' || currentRound === 'ai_voice_3' || currentRound === 'ai_voice_4') ? 'h-full flex flex-col' : 'max-w-4xl mx-auto'">
        <!-- 加载中 -->
        <div v-if="loadingQuestions" class="flex items-center justify-center py-20">
          <div class="border-4 border-black bg-white shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-8 text-center">
            <div class="font-black text-lg mb-2">加载中...</div>
            <div class="font-sans text-sm text-gray-600">正在准备面试题目</div>
          </div>
        </div>

        <!-- 面试已结束 -->
        <div v-else-if="store.currentSession?.status !== 'in_progress'" class="py-10 max-w-xl mx-auto">
          <div class="border-4 border-black bg-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] p-8 text-center">
            <div class="text-5xl mb-4">{{ store.currentSession?.status === 'completed' ? '🎉' : '⛔' }}</div>
            <h2 class="font-black text-2xl mb-2">
              {{ store.currentSession?.status === 'completed' ? '面试完成！' : '面试已中止' }}
            </h2>
            <p class="font-sans text-sm text-gray-600 mb-6">
              {{ store.currentSession?.status === 'completed'
                ? (isSingleMode ? `恭喜你完成了「${targetRoundLabel}」单轮练习。` : '恭喜你完成了全部面试环节。')
                : (abortReason === 'cheat' ? '面试因切屏次数过多被中止。' : '你已手动中止本次面试。') }}
            </p>

            <!-- 报告可用 -->
            <div v-if="reportAvailable" class="flex gap-3 justify-center">
              <button
                class="border-4 border-black bg-[#ff006e] text-white font-black px-6 py-2 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all duration-200"
                @click="goToReport"
              >
                查看评分报告
              </button>
              <button
                class="border-4 border-black bg-white font-black px-6 py-2 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all duration-200"
                @click="router.push('/dashboard')"
              >
                返回岗位选择
              </button>
            </div>

            <!-- 报告不可用（答题不足3题） -->
            <div v-else>
              <div class="border-2 border-black bg-[#ffbe0b] px-4 py-3 mb-4 inline-block">
                <span class="font-black text-sm">📝 答题数量不足3题，未生成评分报告</span>
              </div>
              <div class="flex gap-3 justify-center">
                <button
                  class="border-4 border-black bg-[#ff006e] text-white font-black px-6 py-2 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all duration-200"
                  @click="router.push('/dashboard')"
                >
                  返回岗位选择
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 各轮次组件 -->
        <template v-else>
          <!-- 测评轮次 -->
          <AssessmentRound
            v-if="currentRound === 'assessment'"
            :questions="questions"
            :session-id="sessionId"
            @round-complete="handleRoundComplete"
          />

          <!-- 技术面 -->
          <TechRound
            v-else-if="currentRound === 'tech'"
            :questions="questions"
            :session-id="sessionId"
            @round-complete="handleRoundComplete"
          />

          <!-- 业务面 -->
          <BusinessRound
            v-else-if="currentRound === 'business'"
            :questions="questions"
            :session-id="sessionId"
            @round-complete="handleRoundComplete"
          />

          <!-- AI 语音面试 (三面 / 四面) -->
          <AIVoiceRound
            v-else-if="currentRound === 'ai_voice_3' || currentRound === 'ai_voice_4'"
            :questions="questions"
            :session-id="sessionId"
            :round="currentRound"
            @round-complete="handleRoundComplete"
          />
        </template>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch, provide, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useInterviewStore, type QuestionItem } from '@/stores/interview'
import ProgressSteps from '@/components/interview/ProgressSteps.vue'
import AssessmentRound from '@/components/interview/AssessmentRound.vue'
import TechRound from '@/components/interview/TechRound.vue'
import BusinessRound from '@/components/interview/BusinessRound.vue'
import AIVoiceRound from '@/components/interview/AIVoiceRound.vue'

// ─── 全屏防作弊开关  切屏控制按钮  调节   ─────────────────────────────────────
// 设为 true 启用全屏保护 + ESC拦截 + Keyboard Lock，设为 false 关闭
const ENABLE_FULLSCREEN_PROTECTION = true

const route = useRoute()
const router = useRouter()
const store = useInterviewStore()

const sessionId = computed(() => route.params.id as string)
const currentRound = computed(() => store.currentSession?.current_round || '')
// 是否为选择题轮次（仅选择题显示字体调节）
const isChoiceRound = computed(() => ['assessment', 'business'].includes(currentRound.value))
const isSingleMode = computed(() => store.currentSession?.interview_mode === 'single')
const targetRoundLabel = computed(() => {
  const map: Record<string, string> = {
    assessment: '综合素质测评', tech: '一面·技术面', business: '二面·业务面',
    ai_voice_3: '三面·AI面试', ai_voice_4: '四面·综合面试',
  }
  return store.currentSession?.target_round ? map[store.currentSession.target_round] || store.currentSession.target_round : ''
})
const questions = ref<QuestionItem[]>([])
const loadingQuestions = ref(false)
const cheatCount = ref(0)
const warningMsg = ref('')
const showRules = ref(false)
const rulesAccepted = ref(false)
const reportAvailable = ref(false)
const abortReason = ref<'manual' | 'cheat' | null>(null)
const intentionalFullscreenExit = ref(false) // 标记是否为主动退出全屏
const fontSize = ref(20) // 默认20px
let warningTimer: ReturnType<typeof setTimeout> | null = null

function increaseFont() { fontSize.value = Math.min(fontSize.value + 2, 28) }
function decreaseFont() { fontSize.value = Math.max(fontSize.value - 2, 12) }

// 提供字体大小给子组件
provide('fontSize', fontSize)

// ── 自定义弹窗 ──────────────────────────────────────────────

const confirmModal = reactive({
  show: false,
  title: '',
  message: '',
  confirmText: '确认',
  cancelText: '取消',
  onConfirm: () => { confirmModal.show = false }
})

const alertModal = reactive({
  show: false,
  message: '',
  icon: 'ℹ️'
})

function showAlert(message: string, icon = 'ℹ️') {
  alertModal.message = message
  alertModal.icon = icon
  alertModal.show = true
}

// 提供给子组件使用
provide('showAlert', showAlert)
provide('showConfirm', (opts: { title: string; message: string; onConfirm: () => void }) => {
  confirmModal.title = opts.title
  confirmModal.message = opts.message
  confirmModal.onConfirm = () => { opts.onConfirm(); confirmModal.show = false }
  confirmModal.show = true
})

// ── 防作弊系统 ────────────────────────────────────────────

function showWarning(msg: string) {
  warningMsg.value = msg
  if (warningTimer) clearTimeout(warningTimer)
  warningTimer = setTimeout(() => { warningMsg.value = '' }, 3000)
}

function handleVisibilityChange() {
  if (document.hidden && store.currentSession?.status === 'in_progress') {
    cheatCount.value++
    showWarning(`检测到切屏(${cheatCount.value}/5)，超过5次将自动结束面试`)
    store.reportCheat(sessionId.value, cheatCount.value)
    if (cheatCount.value >= 5) {
      abortReason.value = 'cheat'
      handleAbort(false)
    }
  }
}

function handleFullscreenChange() {
  if (!ENABLE_FULLSCREEN_PROTECTION) return
  if (!document.fullscreenElement && store.currentSession?.status === 'in_progress') {
    if (intentionalFullscreenExit.value) return

    // 弹窗确认是否要离开面试（点击「继续面试」后由 watch 自动恢复全屏）
    confirmModal.title = '离开面试'
    confirmModal.message = '你确定要离开面试吗？离开后面试将被中止。'
    confirmModal.confirmText = '确认离开'
    confirmModal.cancelText = '继续面试'
    confirmModal.onConfirm = async () => {
      confirmModal.show = false
      try {
        intentionalFullscreenExit.value = true
        abortReason.value = 'manual'
        await store.abortInterview(sessionId.value)
        if (document.fullscreenElement) {
          await document.exitFullscreen()
        }
        stopCamera()
        await checkReportAvailable()
      } catch (err) {
        console.error('中止面试失败:', err)
      }
    }
    confirmModal.show = true
  }
}

function handleKeyDown(e: KeyboardEvent) {
  // 禁用 F12 开发者工具
  if (e.key === 'F12') {
    e.preventDefault()
    showWarning('F12 已禁用')
    return
  }
  // 禁用 Ctrl+Shift+I / Ctrl+Shift+J / Ctrl+U 等开发者工具快捷键
  if (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'i' || e.key === 'J' || e.key === 'j' || e.key === 'C' || e.key === 'c')) {
    e.preventDefault()
    showWarning('开发者工具已禁用')
    return
  }
  if (e.ctrlKey && (e.key === 'U' || e.key === 'u')) {
    e.preventDefault()
    showWarning('查看源代码已禁用')
    return
  }
  // ESC 拦截（配合 Keyboard Lock API）
  if (ENABLE_FULLSCREEN_PROTECTION && e.key === 'Escape' && store.currentSession?.status === 'in_progress') {
    e.preventDefault()
    confirmModal.title = '离开面试'
    confirmModal.message = '你确定要离开面试吗？离开后面试将被中止。'
    confirmModal.confirmText = '确认离开'
    confirmModal.cancelText = '继续面试'
    confirmModal.onConfirm = async () => {
      confirmModal.show = false
      try {
        intentionalFullscreenExit.value = true
        abortReason.value = 'manual'
        await store.abortInterview(sessionId.value)
        try { navigator.keyboard?.unlock() } catch { /* 忽略 */ }
        if (document.fullscreenElement) {
          await document.exitFullscreen()
        }
        stopCamera()
        await checkReportAvailable()
      } catch (err) {
        console.error('中止面试失败:', err)
      }
    }
    confirmModal.show = true
    return
  }
  if (
    e.key === 'F12' ||
    (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'J')) ||
    (e.ctrlKey && e.key === 'u')
  ) {
    e.preventDefault()
  }
}

function handleContextMenu(e: MouseEvent) {
  e.preventDefault()
  showWarning('右键已禁用')
}

function handleBeforeUnload(e: BeforeUnloadEvent) {
  if (store.currentSession?.status === 'in_progress') {
    e.preventDefault()
    e.returnValue = '面试进行中，离开将导致面试中止！'
  }
}

function activateAntiCheat() {
  // 强制全屏 + Keyboard Lock
  if (ENABLE_FULLSCREEN_PROTECTION) {
    try {
      document.documentElement.requestFullscreen?.().then(() => {
        try {
          navigator.keyboard?.lock?.(['Escape'])
        } catch { /* 浏览器不支持 Keyboard Lock API */ }
      }).catch(() => { /* 浏览器拒绝全屏 */ })
    } catch { /* 浏览器可能拒绝 */ }
  }

  // 注册防作弊监听
  document.addEventListener('visibilitychange', handleVisibilityChange)
  document.addEventListener('fullscreenchange', handleFullscreenChange)
  document.addEventListener('keydown', handleKeyDown)
  document.addEventListener('contextmenu', handleContextMenu)
  window.addEventListener('beforeunload', handleBeforeUnload)
}

async function acceptRules() {
  showRules.value = false
  rulesAccepted.value = true
  activateAntiCheat()
  await startCamera()   // 启动摄像头
  await loadQuestions()
}

// ── 加载题目 ──────────────────────────────────────────────

async function loadQuestions() {
  loadingQuestions.value = true
  try {
    questions.value = await store.fetchQuestions(sessionId.value)
  } catch (e) {
    console.error('加载题目失败:', e)
  } finally {
    loadingQuestions.value = false
  }
}

// ── 轮次完成 ──────────────────────────────────────────────

async function handleRoundComplete() {
  try {
    const session = await store.nextRound(sessionId.value)
    if (session.status !== 'in_progress') {
      // 面试结束，停止摄像头，检查报告可用性
      stopCamera()
      await checkReportAvailable()
      return
    }
    // 加载下一轮题目
    await loadQuestions()
  } catch (e) {
    console.error('进入下一轮失败:', e)
  }
}

async function handleAbort(manual = true) {
  if (manual) abortReason.value = 'manual'

  // 切屏自动中止：跳过弹窗，直接终止面试
  if (!manual) {
    try {
      await store.abortInterview(sessionId.value)
      stopCamera()
      await checkReportAvailable()
    } catch (e) {
      console.error('自动中止面试失败:', e)
      showAlert('自动中止面试失败，请重试或刷新页面', '❗')
    }
    return
  }

  // 手动中止：弹出确认弹窗
  confirmModal.title = '中止面试'
  confirmModal.message = '确认要中止面试吗？答题数≥3题将生成评分报告。'
  confirmModal.confirmText = '确认中止'
  confirmModal.cancelText = '继续面试'
  confirmModal.onConfirm = async () => {
    confirmModal.show = false
    try {
      await store.abortInterview(sessionId.value)
      stopCamera()
      await checkReportAvailable()
    } catch (e) {
      console.error('中止面试失败:', e)
      showAlert('中止面试失败，请重试', '❗')
    }
  }
  confirmModal.show = true
}

function goToReport() {
  router.push(`/interview/report/${sessionId.value}`)
}

// ── 检查报告是否可用 ────────────────────────────────────────

async function checkReportAvailable() {
  try {
    await store.fetchReport(sessionId.value)
    reportAvailable.value = true
  } catch {
    reportAvailable.value = false
  }
}

// ── 摄像头 & 录制 ───────────────────────────────────────────

const cameraStream = ref<MediaStream | null>(null)
const cameraVideoRef = ref<HTMLVideoElement | null>(null)
const cameraPipRef = ref<HTMLElement | null>(null)
const cameraPipHidden = ref(false)
let mediaRecorder: MediaRecorder | null = null
let recordedChunks: Blob[] = []
let recordingTimer: ReturnType<typeof setInterval> | null = null
const recordingSeconds = ref(0)
const recordingTimeStr = computed(() => {
  const m = Math.floor(recordingSeconds.value / 60).toString().padStart(2, '0')
  const s = (recordingSeconds.value % 60).toString().padStart(2, '0')
  return `${m}:${s}`
})

// PIP 拖动
const cameraPipStyle = reactive({ bottom: '20px', right: '20px', left: 'auto', top: 'auto' })
let pipDragStart = { x: 0, y: 0, pipX: 0, pipY: 0, dragging: false }

function startDragPip(e: MouseEvent) {
  e.preventDefault()
  const el = cameraPipRef.value
  if (!el) return
  const rect = el.getBoundingClientRect()
  pipDragStart = { x: e.clientX, y: e.clientY, pipX: rect.left, pipY: rect.top, dragging: true }
  document.addEventListener('mousemove', onDragPip)
  document.addEventListener('mouseup', stopDragPip)
}

function onDragPip(e: MouseEvent) {
  if (!pipDragStart.dragging) return
  const dx = e.clientX - pipDragStart.x
  const dy = e.clientY - pipDragStart.y
  cameraPipStyle.left = `${pipDragStart.pipX + dx}px`
  cameraPipStyle.top = `${pipDragStart.pipY + dy}px`
  cameraPipStyle.right = 'auto'
  cameraPipStyle.bottom = 'auto'
}

function stopDragPip() {
  pipDragStart.dragging = false
  document.removeEventListener('mousemove', onDragPip)
  document.removeEventListener('mouseup', stopDragPip)
}

async function startCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { width: 640, height: 480, facingMode: 'user' },
      audio: false  // 仅录视频，避免与 SpeechRecognition 争用麦克风
    })
    cameraStream.value = stream
    await nextTick()
    if (cameraVideoRef.value) {
      cameraVideoRef.value.srcObject = stream
    }
    // 开始录制（不上传，仅本地保留）
    recordedChunks = []
    recordingSeconds.value = 0
    try {
      mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/webm;codecs=vp9' })
    } catch {
      try {
        mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/webm' })
      } catch {
        mediaRecorder = new MediaRecorder(stream)
      }
    }
    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) recordedChunks.push(e.data)
    }
    mediaRecorder.onstop = () => {
      console.log('录制完成，时长:', recordingSeconds.value, '秒')
    }
    mediaRecorder.start(1000)
    recordingTimer = setInterval(() => { recordingSeconds.value++ }, 1000)
  } catch (e) {
    console.error('摄像头启动失败:', e)
    showAlert('摄像头启动失败：' + (e as Error).message + '，请确保已授权摄像头权限', '📷')
  }
}

function stopCamera() {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
  }
  if (recordingTimer) {
    clearInterval(recordingTimer)
    recordingTimer = null
  }
  if (cameraStream.value) {
    cameraStream.value.getTracks().forEach(t => t.stop())
    cameraStream.value = null
  }
}

// ── 监听轮次变化 ──────────────────────────────────────────

watch(currentRound, async (newRound, oldRound) => {
  if (newRound && newRound !== oldRound && store.currentSession?.status === 'in_progress') {
    await loadQuestions()
  }
})

// ── 弹窗关闭后自动恢复全屏 ────────────────────────────
watch(
  () => confirmModal.show,
  async (newVal, oldVal) => {
    if (oldVal === true && newVal === false &&
        store.currentSession?.status === 'in_progress' &&
        ENABLE_FULLSCREEN_PROTECTION &&
        !document.fullscreenElement) {
      // 用户点击了「继续面试」或关闭了弹窗，重新进入全屏
      await nextTick()
      document.documentElement.requestFullscreen?.().catch(() => {})
    }
  }
)

// ── 生命周期 ──────────────────────────────────────────────

onMounted(async () => {
  // 加载会话状态
  await store.fetchSession(sessionId.value)

  if (store.currentSession?.status === 'in_progress') {
    // 显示入场须知，等待用户确认后再进入全屏
    showRules.value = true
  } else {
    // 已结束，检查报告是否可用，然后加载题目
    await checkReportAvailable()
    await loadQuestions()
  }
})

onUnmounted(() => {
  // 停止摄像头和录制
  stopCamera()

  // 解锁键盘
  if (ENABLE_FULLSCREEN_PROTECTION) {
    try { navigator.keyboard?.unlock() } catch { /* 忽略 */ }
  }

  // 移除防作弊监听
  document.removeEventListener('visibilitychange', handleVisibilityChange)
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  document.removeEventListener('keydown', handleKeyDown)
  document.removeEventListener('contextmenu', handleContextMenu)
  window.removeEventListener('beforeunload', handleBeforeUnload)

  // 移除 PIP 拖动监听
  document.removeEventListener('mousemove', onDragPip)
  document.removeEventListener('mouseup', stopDragPip)

  // 退出全屏
  if (ENABLE_FULLSCREEN_PROTECTION && document.fullscreenElement) {
    document.exitFullscreen?.()
  }

  if (warningTimer) clearTimeout(warningTimer)
})
</script>
