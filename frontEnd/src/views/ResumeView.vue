<template>
  <div class="h-screen w-screen flex flex-col overflow-hidden bg-memphis-cream">
    <!-- 顶部导航栏 -->
    <nav class="shrink-0 bg-white border-b-4 border-black px-6 py-1.5 flex items-center justify-between z-50">
      <div class="flex items-center gap-4">
        <router-link
          to="/dashboard"
          class="flex items-center gap-2 px-3 py-1.5 border-4 border-black bg-white font-black text-sm hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200"
        >
          ← 返回仪表盘
        </router-link>
        <div class="flex items-center gap-2">
          <div class="w-7 h-7 bg-memphis-purple border-2 border-black flex items-center justify-center">
            <span class="text-sm">📄</span>
          </div>
          <span class="font-black text-xl tracking-tight">简历分析</span>
        </div>
      </div>

      <!-- 有简历时的右侧按钮 -->
      <div v-if="resumeStore.hasResume" class="flex items-center gap-2">
        <span class="font-mono text-sm px-3 py-1 border-2 border-black bg-memphis-yellow">
          ✓ {{ resumeStore.resume?.file_name }}
        </span>
        <button
          class="px-4 py-1.5 border-4 border-black bg-white font-black text-sm shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200"
          @click="showUploadModal = true"
        >
          📎 上传新简历
        </button>
        <router-link
          to="/resume/optimize"
          class="px-4 py-1.5 border-4 border-black bg-memphis-orange text-white font-black text-sm shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200"
        >
          ✨ 措辞优化
        </router-link>
        <button
          v-if="!resumeStore.analyzing && !resumeStore.hasParsedContent"
          class="px-4 py-1.5 border-4 border-black bg-memphis-purple text-white font-black text-sm shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200"
          @click="handleAnalyze"
        >
          🔍 AI 分析
        </button>
        <button v-else-if="resumeStore.analyzing" class="px-4 py-1.5 border-4 border-black bg-black text-white font-black text-sm" disabled>
          ⏳ 分析中...
        </button>
        <button
          class="px-4 py-1.5 border-4 border-black bg-memphis-yellow font-black text-sm shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200"
          @click="handleViewRawText"
        >
          📝 简历原文
        </button>
      </div>

      <!-- 无简历时的右侧提示 -->
      <div v-else class="flex items-center gap-2">
        <span class="font-mono text-sm text-gray-600">请先上传简历</span>
      </div>
    </nav>

    <!-- ═══ 状态 A：无简历 - 居中上传 ═══ -->
    <main v-if="!resumeStore.hasResume && !resumeStore.loading" class="flex-1 flex items-center justify-center p-8">
      <div class="w-full max-w-2xl">
        <!-- 标题 -->
        <div class="text-center mb-8">
          <div class="inline-flex w-16 h-16 bg-memphis-purple border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] items-center justify-center mb-4">
            <span class="text-3xl">📄</span>
          </div>
          <h1 class="font-black text-3xl tracking-tight mb-2">上传你的简历</h1>
          <p class="font-mono text-base text-gray-600">支持 PDF / DOCX 格式，AI 将自动提取结构化信息</p>
        </div>

        <!-- 上传区域 -->
        <div
          class="border-4 border-dashed border-black bg-white p-12 flex flex-col items-center justify-center cursor-pointer hover:bg-memphis-yellow/10 transition-colors shadow-[5px_5px_0px_0px_rgba(0,0,0,1)]"
          @click="triggerUpload"
          @dragover.prevent="dragOver = true"
          @dragleave="dragOver = false"
          @drop.prevent="handleDrop"
          :class="dragOver ? 'bg-memphis-yellow/20 border-memphis-coral' : ''"
        >
          <div class="text-5xl mb-4">📁</div>
          <div class="font-black text-xl mb-2">点击或拖拽上传简历</div>
          <div class="font-mono text-base text-gray-600">PDF / DOCX 格式，最大 10MB</div>
          <input ref="fileInput" type="file" accept=".pdf,.docx" class="hidden" @change="handleFileChange" />
        </div>

        <!-- 解析中提示 -->
        <div v-if="parsing" class="mt-6 text-center">
          <div class="font-black text-base text-memphis-purple animate-pulse">⏳ 正在解析简历内容...</div>
        </div>

        <!-- API Key 提示 -->
        <div v-if="!resumeStore.hasApiKey" class="mt-6 border-4 border-black bg-white p-4 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]">
          <div class="flex items-center gap-3">
            <span class="w-8 h-8 bg-memphis-coral border-2 border-black flex items-center justify-center text-base shrink-0">⚠️</span>
            <div class="flex-1">
              <div class="font-black text-sm mb-1">Deepseek API 尚未配置</div>
              <div class="font-mono text-xs text-gray-600">请联系管理员在后端 .env 文件中设置 DEEPSEEK_API_KEY 以启用 AI 分析功能</div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 加载中 -->
    <main v-else-if="resumeStore.loading && !resumeStore.hasResume" class="flex-1 flex items-center justify-center">
      <div class="font-black text-xl text-memphis-purple animate-pulse">⏳ 加载简历中...</div>
    </main>

    <!-- ═══ 状态 B：有简历 - 双栏分析 ═══ -->
    <main v-else-if="resumeStore.hasResume" class="flex-1 overflow-hidden p-4 flex gap-4 min-h-0">
      <!-- 左侧：结构化提取 (1/3) -->
      <section class="w-1/3 bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] flex flex-col overflow-hidden">
        <div class="shrink-0 px-4 py-2.5 border-b-4 border-black bg-memphis-cream flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="text-base">🤖</span>
            <h2 class="font-black text-lg tracking-tight">结构化提取</h2>
          </div>
          <span class="font-mono text-sm px-2 py-0.5 border-2 border-black bg-memphis-yellow">AI 提取</span>
        </div>

        <!-- 无分析结果时的提示 -->
        <div v-if="!resumeStore.hasParsedContent" class="flex-1 flex flex-col items-center justify-center p-6 text-center">
          <div class="text-4xl mb-3">🤖</div>
          <div class="font-black text-base mb-2">尚未进行 AI 分析</div>
          <div v-if="resumeStore.hasApiKey" class="font-mono text-sm text-gray-600 mb-4">点击顶部「AI 分析」按钮开始</div>
          <div v-else>
            <div class="font-mono text-sm text-memphis-coral mb-2">Deepseek API 尚未配置</div>
            <div class="font-mono text-sm text-gray-600">请在后端 .env 中设置 DEEPSEEK_API_KEY</div>
          </div>
        </div>

        <!-- 有分析结果 -->
        <div v-else class="flex-1 overflow-y-auto p-4 space-y-4">
          <!-- 技能关键词 -->
          <div>
            <div class="font-black text-base mb-2 flex items-center gap-1.5">
              <span class="w-3 h-3 bg-memphis-purple border border-black inline-block shrink-0" />
              技能关键词
            </div>
            <div class="flex flex-wrap gap-1.5">
              <span
                v-for="skill in parsed?.skills"
                :key="skill"
                class="font-mono text-sm px-2 py-0.5 border-2 border-black bg-memphis-purple/10 font-bold"
              >{{ skill }}</span>
            </div>
          </div>

          <!-- 工作经历 -->
          <div>
            <div class="font-black text-base mb-2 flex items-center gap-1.5">
              <span class="w-3 h-3 bg-memphis-coral border border-black inline-block shrink-0" />
              工作经历
            </div>
            <div class="space-y-1.5">
              <div v-for="(exp, idx) in parsed?.experiences" :key="idx" class="border-2 border-black p-2.5 bg-memphis-cream">
                <div class="flex items-center justify-between">
                  <span class="font-black text-sm">{{ exp.role }}</span>
                  <span class="font-mono text-sm text-gray-600">{{ exp.duration }}</span>
                </div>
                <div class="font-mono text-sm text-gray-700">{{ exp.company }} · {{ exp.period }}</div>
                <div v-if="exp.description" class="font-mono text-sm text-gray-600 mt-1">{{ exp.description }}</div>
              </div>
            </div>
          </div>

          <!-- 教育背景 -->
          <div>
            <div class="font-black text-base mb-2 flex items-center gap-1.5">
              <span class="w-3 h-3 bg-memphis-blue border border-black inline-block shrink-0" />
              教育背景
            </div>
            <div class="space-y-1.5">
              <div v-for="(edu, idx) in parsed?.education" :key="idx" class="border-2 border-black p-2.5 bg-memphis-cream">
                <div class="font-black text-sm">{{ edu.school }}</div>
                <div class="font-mono text-sm text-gray-700">{{ edu.degree }} · {{ edu.period }}</div>
              </div>
            </div>
          </div>

        </div>
      </section>

      <!-- 右侧：简历报告 (2/3) -->
      <section class="w-2/3 bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] flex flex-col overflow-hidden">
        <!-- 无分析结果时的占位 -->
        <div v-if="!resumeStore.hasParsedContent" class="flex-1 flex flex-col items-center justify-center text-center p-8">
          <div class="text-5xl mb-4">📊</div>
          <div class="font-black text-xl mb-2">简历报告</div>
          <div class="font-mono text-base text-gray-600">完成 AI 分析后将在此展示完整简历报告</div>
        </div>

        <!-- 有分析结果 -->
        <div v-else class="flex-1 overflow-y-auto p-5">
          <div class="grid grid-cols-3 gap-5">
            <!-- 综合评分 -->
            <div class="col-span-1 flex flex-col">
              <div class="font-black text-lg mb-3 flex items-center gap-1.5">
                <span class="w-4 h-4 bg-memphis-coral border-2 border-black inline-block shrink-0" />
                综合评分
              </div>
              <div class="border-4 border-black bg-memphis-cream p-5 text-center flex-1 flex flex-col justify-center">
                <div class="font-black text-5xl text-memphis-coral">{{ parsed?.score || 0 }}</div>
                <div class="font-mono text-base text-gray-600 mt-1">总分 / 100</div>
                <div class="mt-3 h-3 border-2 border-black bg-white overflow-hidden">
                  <div class="h-full bg-memphis-coral transition-all duration-500" :style="{ width: (parsed?.score || 0) + '%' }" />
                </div>
              </div>
            </div>

            <!-- 技能词云大图 -->
            <div class="col-span-2 flex flex-col">
              <div class="font-black text-lg mb-3 flex items-center gap-1.5">
                <span class="w-4 h-4 bg-memphis-purple border-2 border-black inline-block shrink-0" />
                技能词云
              </div>
              <div class="border-4 border-black bg-memphis-cream p-6 flex-1 flex flex-wrap items-center justify-center gap-x-4 gap-y-3 min-h-32">
                <span
                  v-for="word in wordCloudItems"
                  :key="word.text"
                  class="font-black leading-none"
                  :style="{ fontSize: word.size + 'px', color: word.color }"
                >{{ word.text }}</span>
                <span v-if="!wordCloudItems.length" class="font-mono text-base text-gray-600">暂无技能数据</span>
              </div>
            </div>

            <!-- 经历时间线 -->
            <div class="col-span-1">
              <div class="font-black text-lg mb-3 flex items-center gap-1.5">
                <span class="w-4 h-4 bg-memphis-blue border-2 border-black inline-block shrink-0" />
                经历时间线
              </div>
              <div class="space-y-3">
                <div v-for="(exp, idx) in parsed?.experiences" :key="idx" class="border-2 border-black p-4 bg-memphis-cream">
                  <div class="flex items-center gap-2 mb-1.5">
                    <span class="w-3 h-3 border-2 border-black shrink-0" :style="{ backgroundColor: timelineColors[idx % 4] }" />
                    <span class="font-black text-lg">{{ exp.role }}</span>
                  </div>
                  <div class="font-mono text-base text-gray-600 ml-5">{{ exp.period }}</div>
                  <div class="font-mono text-base text-gray-700 ml-5 mt-0.5">{{ exp.company }}</div>
                </div>
              </div>
            </div>

            <!-- 技能分布 -->
            <div class="col-span-1">
              <div class="font-black text-lg mb-3 flex items-center gap-1.5">
                <span class="w-4 h-4 bg-memphis-yellow border-2 border-black inline-block shrink-0" />
                技能分布
              </div>
              <div class="space-y-3">
                <div v-for="cat in parsed?.skill_categories" :key="cat.name" class="border-2 border-black p-3 bg-memphis-cream">
                  <div class="flex items-center justify-between mb-1.5">
                    <span class="font-black text-base">{{ cat.name }}</span>
                    <span class="font-mono text-base px-1.5 py-0.5 border border-black bg-white">{{ Math.round((cat.percent || 0) / 10) }} / 10</span>
                  </div>
                  <div class="h-3 border border-black bg-white overflow-hidden">
                    <div class="h-full" :style="{ width: (Math.round((cat.percent || 0) / 10) * 10) + '%', backgroundColor: categoryColors[cat.name] || '#ff006e' }" />
                  </div>
                </div>
              </div>
            </div>

            <!-- 改进建议 -->
            <div class="col-span-1">
              <div class="font-black text-lg mb-3 flex items-center gap-1.5">
                <span class="w-4 h-4 bg-memphis-orange border-2 border-black inline-block shrink-0" />
                改进建议
              </div>
              <div class="space-y-3">
                <div v-for="(sug, idx) in parsed?.suggestions" :key="idx" class="border-2 border-black p-3 bg-memphis-cream">
                  <div class="flex items-start gap-2">
                    <span class="font-black text-base shrink-0 mt-0.5" :class="suggestionColor(sug.type)">{{ suggestionIcon(sug.type) }}</span>
                    <div>
                      <div class="font-black text-sm">{{ sug.title }}</div>
                      <div class="font-mono text-sm text-gray-700 mt-0.5">{{ sug.desc }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- ═══ 上传新简历弹窗 ═══ -->
    <teleport to="body">
      <div v-if="showUploadModal" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/40" @click.self="showUploadModal = false">
        <div class="bg-white border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] w-full max-w-lg p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-black text-xl tracking-tight">📎 上传新简历</h3>
            <button class="w-8 h-8 border-4 border-black bg-memphis-coral text-white font-black text-base flex items-center justify-center hover:bg-black transition-colors" @click="showUploadModal = false">✕</button>
          </div>
          <p class="font-mono text-sm text-gray-600 mb-4">上传新简历将覆盖当前已保存的简历数据，请确认。</p>
          <div
            class="border-4 border-dashed border-black bg-memphis-cream p-8 flex flex-col items-center justify-center cursor-pointer hover:bg-memphis-yellow/20 transition-colors"
            @click="triggerModalUpload"
            @dragover.prevent
            @drop.prevent="handleModalDrop"
          >
            <div class="text-3xl mb-2">📁</div>
            <div class="font-black text-base mb-1">点击或拖拽上传</div>
            <div class="font-mono text-xs text-gray-600">PDF / DOCX，最大 10MB</div>
            <input ref="modalFileInput" type="file" accept=".pdf,.docx" class="hidden" @change="handleModalFileChange" />
          </div>
          <div v-if="modalParsing" class="mt-3 text-center">
            <div class="font-black text-sm text-memphis-purple animate-pulse">⏳ 正在解析并保存...</div>
          </div>
          <div v-if="modalFileName" class="mt-3 flex items-center gap-2">
            <span class="font-mono text-sm px-3 py-1 border-2 border-black bg-memphis-yellow">✓ {{ modalFileName }}</span>
          </div>
        </div>
      </div>
    </teleport>

    <!-- ═══ Word 下载提示 Toast ═══ -->
    <teleport to="body">
      <div v-if="rawTextToast" class="fixed bottom-8 left-1/2 -translate-x-1/2 z-[200] bg-black text-white font-black text-sm px-6 py-3 border-4 border-black shadow-[5px_5px_0px_0px_rgba(255,190,11,1)] flex items-center gap-2 transition-all">
        <span>✅</span> Word 源文件已下载
      </div>
    </teleport>

    <!-- ═══ 简历原文弹窗（仅 PDF） ═══ -->
    <teleport to="body">
      <div v-if="showRawTextModal" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/40" @click.self="showRawTextModal = false">
        <div class="bg-white border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] w-full max-w-4xl h-[95vh] flex flex-col">
          <div class="shrink-0 flex items-center justify-between px-5 py-3 border-b-4 border-black bg-memphis-yellow">
            <h3 class="font-black text-xl tracking-tight flex items-center gap-2">
              <span>📝</span> 简历原文
            </h3>
            <button class="w-8 h-8 border-4 border-black bg-memphis-coral text-white font-black text-base flex items-center justify-center hover:bg-black transition-colors" @click="showRawTextModal = false">✕</button>
          </div>
          <div class="flex-1 overflow-hidden">
            <iframe
              v-if="resumeStore.resume?.file_path"
              :src="'/api/' + resumeStore.resume.file_path"
              class="w-full h-full"
              style="min-height: 85vh;"
            />
            <div v-else class="p-5">
              <pre class="font-mono text-base leading-relaxed whitespace-pre-wrap break-words">{{ resumeStore.resume?.raw_text }}</pre>
            </div>
          </div>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useResumeStore } from '@/stores/resume'
import type { ParsedContent } from '@/stores/resume'

// ── Store ────────────────────────────────────────────────
const resumeStore = useResumeStore()

// ── 状态 ─────────────────────────────────────────────────
const fileInput = ref<HTMLInputElement | null>(null)
const modalFileInput = ref<HTMLInputElement | null>(null)
const dragOver = ref(false)
const parsing = ref(false)
const modalParsing = ref(false)
const modalFileName = ref('')
const showUploadModal = ref(false)
const showRawTextModal = ref(false)
const rawTextToast = ref(false)

// ── Computed ─────────────────────────────────────────────
const parsed = computed<ParsedContent | null>(() => resumeStore.resume?.parsed_content || null)

// 词云：根据技能列表动态生成
const memphisColors = ['#ff006e', '#3a86ff', '#8338ec', '#fb5607', '#ffbe0b']
const wordCloudItems = computed(() => {
  const skills = parsed.value?.skills || []
  return skills.map((skill, idx) => ({
    text: skill,
    size: Math.max(18, 42 - idx * 2),
    color: memphisColors[idx % memphisColors.length],
  }))
})

const timelineColors = ['#ff006e', '#3a86ff', '#ffbe0b', '#8338ec']

const categoryColors: Record<string, string> = {
  '前端框架': '#ff006e',
  '后端技术': '#3a86ff',
  '构建工具': '#ffbe0b',
  'DevOps': '#8338ec',
  '数据库': '#fb5607',
}

function suggestionColor(type: string): string {
  if (type === 'success') return 'text-[#22c55e]'
  if (type === 'info') return 'text-memphis-blue'
  return 'text-memphis-coral'
}

function suggestionIcon(type: string): string {
  if (type === 'success') return '✅'
  if (type === 'info') return '💡'
  return '⚠️'
}

// ── 生命周期 ─────────────────────────────────────────────
onMounted(async () => {
  await Promise.all([resumeStore.fetchResume(), resumeStore.fetchConfig()])
})

// ── 文件解析工具 ─────────────────────────────────────────
async function extractTextFromFile(file: File): Promise<string> {
  const ext = file.name.split('.').pop()?.toLowerCase()
  if (ext === 'pdf') {
    // 使用后端 PyMuPDF 提取，比前端 pdf.js 更可靠
    return await resumeStore.extractPdfText(file)
  } else if (ext === 'docx') {
    const mammoth = await import('mammoth')
    const arrayBuffer = await file.arrayBuffer()
    const result = await mammoth.extractRawText({ arrayBuffer })
    return result.value.trim()
  }
  throw new Error('不支持的文件格式')
}

// ── 主页上传 ─────────────────────────────────────────────
function triggerUpload() {
  fileInput.value?.click()
}

async function handleFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  await processUpload(file)
}

async function handleDrop(e: DragEvent) {
  dragOver.value = false
  const file = e.dataTransfer?.files[0]
  if (!file) return
  await processUpload(file)
}

async function processUpload(file: File) {
  parsing.value = true
  try {
    const text = await extractTextFromFile(file)
    await resumeStore.uploadResume(file, text)
  } catch (err) {
    alert(`上传失败: ${(err as Error).message}`)
  } finally {
    parsing.value = false
  }
}

// ── 弹窗上传 ─────────────────────────────────────────────
function triggerModalUpload() {
  modalFileInput.value?.click()
}

async function handleModalFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  await processModalUpload(file)
}

async function handleModalDrop(e: DragEvent) {
  const file = e.dataTransfer?.files[0]
  if (!file) return
  await processModalUpload(file)
}

async function processModalUpload(file: File) {
  modalParsing.value = true
  modalFileName.value = file.name
  try {
    const text = await extractTextFromFile(file)
    await resumeStore.uploadResume(file, text)
    showUploadModal.value = false
  } catch (err) {
    alert(`上传失败: ${(err as Error).message}`)
  } finally {
    modalParsing.value = false
  }
}

// ── 简历原文查看 ─────────────────────────────────────────
function isWordFile(): boolean {
  const name = resumeStore.resume?.file_name || ''
  return name.toLowerCase().endsWith('.docx')
}

function handleViewRawText() {
  if (isWordFile()) {
    // Word 文件：直接下载，不弹窗
    downloadWordFile()
  } else {
    showRawTextModal.value = true
  }
}

function downloadWordFile() {
  const filePath = resumeStore.resume?.file_path
  if (!filePath) return
  const link = document.createElement('a')
  link.href = '/api/' + filePath
  link.download = resumeStore.resume?.file_name || 'resume.docx'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  // 显示下载提示
  rawTextToast.value = true
  setTimeout(() => { rawTextToast.value = false }, 3000)
}

// ── AI 分析 ──────────────────────────────────────────────
async function handleAnalyze() {
  try {
    await resumeStore.analyzeResume()
  } catch (err) {
    alert(`分析失败: ${(err as Error).message}`)
  }
}
</script>
