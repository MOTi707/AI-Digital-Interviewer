<template>
  <div class="h-screen w-screen flex flex-col overflow-hidden bg-memphis-cream">
    <!-- 隐藏的简历打印区域 -->
    <div id="resume-print" class="resume-print-root">
      <div class="resume-page">
        <!-- 头部 -->
        <div class="resume-header">
          <div class="resume-avatar" :style="!user?.avatar ? { backgroundColor: user?.avatar_color || '#ff006e' } : {}">
            <img v-if="user?.avatar" :src="`/${user?.avatar}`" class="w-full h-full object-cover" alt="avatar" />
            <span v-else class="resume-avatar-letter">{{ avatarText }}</span>
          </div>
          <div class="resume-header-info">
            <h1 class="resume-name">{{ user?.nickname || user?.username || '用户' }}</h1>
            <div class="resume-meta">
              <span>📱 {{ user?.phone || '未填写' }}</span>
              <span>✉️ {{ user?.email || '未填写' }}</span>
              <span>🎂 {{ user?.birth_date || '未填写' }}</span>
              <span>👤 {{ genderLabel(user?.gender) }}</span>
            </div>
            <div class="resume-target">
              <span class="resume-target-label">意向岗位</span>
              <span class="resume-target-value">程序员</span>
            </div>
          </div>
        </div>

        <div class="resume-divider"></div>

        <!-- 个人简介 -->
        <div v-if="user?.bio" class="resume-section">
          <h2 class="resume-section-title">个人简介</h2>
          <p class="resume-text">{{ user.bio }}</p>
        </div>

        <!-- 实习经历（虚构） -->
        <div class="resume-section">
          <h2 class="resume-section-title">实习经历</h2>
          <div class="resume-exp">
            <div class="resume-exp-header">
              <span class="resume-exp-company">XX互联网科技有限公司</span>
              <span class="resume-exp-date">2025.07 - 2025.12</span>
            </div>
            <div class="resume-exp-role">软件开发实习生</div>
            <ul class="resume-exp-list">
              <li>参与公司内部管理系统的前后端开发与维护，使用 Vue.js + FastAPI 技术栈，独立完成多个功能模块的设计与实现</li>
              <li>负责 RESTful API 接口设计与开发，优化数据库查询性能，接口平均响应时间降低约 40%</li>
              <li>参与代码评审和单元测试编写，累计编写测试用例 50+，代码覆盖率提升至 85% 以上</li>
              <li>协助团队完成项目从需求分析到上线部署的全流程，积累了敏捷开发与团队协作的实战经验</li>
            </ul>
          </div>
        </div>

        <!-- 教育背景 -->
        <div class="resume-section">
          <h2 class="resume-section-title">教育背景</h2>
          <div class="resume-exp">
            <div class="resume-exp-header">
              <span class="resume-exp-company">XX大学 · 计算机科学与技术</span>
              <span class="resume-exp-date">2022.09 - 2026.06（在读）</span>
            </div>
          </div>
        </div>

        <!-- 技能 -->
        <div class="resume-section">
          <h2 class="resume-section-title">专业技能</h2>
          <ul class="resume-exp-list">
            <li>熟练掌握 Python、JavaScript/TypeScript 等编程语言，熟悉面向对象编程和设计模式</li>
            <li>熟悉 Vue.js、React 等前端框架，具备完整的前端工程化开发经验</li>
            <li>熟悉 FastAPI、Flask 等后端框架，了解 MySQL、PostgreSQL 等关系型数据库</li>
            <li>了解 Git 版本控制、Linux 系统操作、Docker 容器化部署等开发工具链</li>
          </ul>
        </div>

        <!-- 职业测评结果 -->
        <div v-if="hasAssessmentResults" class="resume-section">
          <h2 class="resume-section-title">职业倾向测评</h2>

          <!-- Holland -->
          <div v-if="hollandRecord" class="resume-assess-block">
            <div class="resume-assess-title">Holland 六维度职业兴趣测评</div>
            <div class="resume-assess-result">
              <span class="resume-assess-label">Holland 代码</span>
              <span class="resume-assess-value">{{ hollandCode }}</span>
            </div>
            <div class="resume-assess-tags">
              <span v-for="d in hollandTop3" :key="d.code" class="resume-tag">
                {{ d.code }} · {{ d.name.replace(/ \(.+\)/, '') }}
              </span>
            </div>
            <p class="resume-assess-summary">{{ hollandRecord.summary }}</p>
          </div>

          <!-- MBTI -->
          <div v-if="mbtiRecord" class="resume-assess-block">
            <div class="resume-assess-title">MBTI 性格类型测评</div>
            <div class="resume-assess-result">
              <span class="resume-assess-label">性格类型</span>
              <span class="resume-assess-value resume-mbti-type">{{ mbtiType }}</span>
              <span class="resume-assess-sub">{{ mbtiInfo?.name }}</span>
            </div>
            <p class="resume-assess-summary">{{ mbtiRecord.summary }}</p>
          </div>

          <!-- 职业价值观 -->
          <div v-if="cvRecord" class="resume-assess-block">
            <div class="resume-assess-title">职业价值观测评</div>
            <div class="resume-assess-result">
              <span class="resume-assess-label">核心价值观</span>
              <span class="resume-assess-value">{{ cvCoreNames }}</span>
            </div>
            <p class="resume-assess-summary">{{ cvRecord.summary }}</p>
          </div>
        </div>

        <!-- 页脚 -->
        <div class="resume-footer">
          <span>本简历由 AI面试官平台 自动生成 · {{ todayStr }}</span>
        </div>
      </div>
    </div>

    <!-- 顶部导航栏 -->
    <nav class="shrink-0 bg-white border-b-2 border-black px-6 py-2 flex items-center justify-between z-50">
      <div class="flex items-center gap-6">
        <router-link to="/" class="font-black text-xl tracking-tight flex items-center gap-2 shrink-0">
          <span class="inline-block w-7 h-7 bg-memphis-coral border-2 border-black" />
          <span>AI面试官</span>
        </router-link>
      </div>
      <div class="flex items-center gap-3">
        <router-link
          to="/dashboard"
          class="px-4 py-2 font-black text-sm border-2 border-black bg-white shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:shadow-[1px_1px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[1px] hover:translate-y-[1px] transition-all duration-200"
        >
          ← 返回仪表盘
        </router-link>
      </div>
    </nav>

    <!-- 主内容区域 -->
    <main class="flex-1 overflow-y-auto p-8">
      <div class="max-w-5xl mx-auto space-y-8">
        <!-- 顶部：头像卡片 + 编辑表单 -->
        <div class="grid grid-cols-12 gap-8">
          <!-- 左侧：头像信息卡片 -->
          <div class="col-span-4">
            <div class="bg-white border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] p-8">
              <!-- 大头像 -->
              <div class="flex flex-col items-center">
                <!-- 头像显示区域 -->
                <div
                  class="relative w-32 h-32 border-2 border-black flex items-center justify-center font-black text-6xl text-white shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] cursor-pointer group overflow-hidden"
                  :style="!avatarPreview && !user?.avatar ? { backgroundColor: previewColor || user?.avatar_color || '#ff006e' } : {}"
                  @click="triggerAvatarUpload"
                >
                  <!-- 已有头像图片 -->
                  <img
                    v-if="avatarPreview || user?.avatar"
                    :src="avatarPreview || `/${user?.avatar}`"
                    class="w-full h-full object-cover"
                    alt="头像"
                  />
                  <!-- 无头像时显示首字母 -->
                  <span v-else>{{ avatarText }}</span>

                  <!-- 悬停遮罩 -->
                  <div class="absolute inset-0 bg-black/50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <span class="text-white font-black text-sm">更换头像</span>
                  </div>
                </div>

                <!-- 隐藏的文件输入 -->
                <input
                  ref="avatarInput"
                  type="file"
                  accept="image/jpeg,image/png,image/webp,image/gif"
                  class="hidden"
                  @change="handleAvatarUpload"
                />

                <!-- 上传状态提示 -->
                <p v-if="avatarUploading" class="font-mono text-sm text-gray-600 mt-3">上传中...</p>
                <p v-else class="font-mono text-sm text-gray-600 mt-3">点击更换头像</p>

                <h2 class="font-black text-2xl tracking-tight mt-3">{{ user?.nickname || user?.username || '用户' }}</h2>
                <p class="font-mono text-base text-gray-700 mt-2">@{{ user?.username }}</p>
                <p class="font-mono text-sm text-gray-600 mt-2">{{ user?.email || '未设置邮箱' }}</p>
              </div>

              <!-- 信息列表 -->
              <div class="mt-8 space-y-4 border-t border-black pt-5">
                <div class="flex items-center justify-between">
                  <span class="font-mono text-sm text-gray-600">注册时间</span>
                  <span class="font-black text-sm">{{ formatDate(user?.created_at) }}</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="font-mono text-sm text-gray-600">手机号</span>
                  <span class="font-black text-sm">{{ user?.phone || '未设置' }}</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="font-mono text-sm text-gray-600">性别</span>
                  <span class="font-black text-sm">{{ genderLabel(user?.gender) }}</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="font-mono text-sm text-gray-600">生日</span>
                  <span class="font-black text-sm">{{ user?.birth_date || '未设置' }}</span>
                </div>
              </div>
            </div>

            <!-- 导出简历PDF按钮 -->
            <button
              :disabled="exporting"
              class="w-full mt-4 py-3 font-black text-sm border-2 border-black bg-memphis-yellow shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:shadow-[1px_1px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[1px] hover:translate-y-[1px] transition-all duration-200 disabled:cursor-not-allowed"
              @click="handleExportPdf"
            >
              {{ exporting ? '⏳ 生成中...' : '📄 导出简历PDF' }}
            </button>
          </div>

          <!-- 右侧：编辑表单 -->
          <div class="col-span-8">
            <div class="bg-white border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] p-8">
              <h3 class="font-black text-2xl tracking-tight mb-6">编辑个人资料</h3>

              <form @submit.prevent="handleSaveProfile" class="space-y-5">
                <!-- 昵称 -->
                <div>
                  <label class="block font-black text-base mb-2">昵称</label>
                  <input
                    v-model="profileForm.nickname"
                    type="text"
                    placeholder="输入你的昵称"
                    class="w-full border-2 border-black bg-white px-4 py-3 font-mono text-base focus:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] focus:outline-none transition-all"
                  />
                </div>

                <!-- 个人简介 -->
                <div>
                  <label class="block font-black text-base mb-2">个人简介</label>
                  <textarea
                    v-model="profileForm.bio"
                    rows="3"
                    placeholder="介绍一下自己..."
                    class="w-full border-2 border-black bg-white px-4 py-3 font-mono text-base focus:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] focus:outline-none transition-all resize-none"
                  />
                </div>

                <!-- 手机号 + 性别 -->
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block font-black text-base mb-2">手机号</label>
                    <input
                      v-model="profileForm.phone"
                      type="tel"
                      placeholder="输入手机号"
                      class="w-full border-2 border-black bg-white px-4 py-3 font-mono text-base focus:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] focus:outline-none transition-all"
                    />
                  </div>
                  <div>
                    <label class="block font-black text-base mb-2">性别</label>
                    <div class="flex gap-3">
                      <button
                        v-for="g in genderOptions"
                        :key="g.value"
                        type="button"
                        :class="[
                          'flex-1 py-3 border-2 border-black font-black text-sm transition-all duration-200',
                          profileForm.gender === g.value
                            ? g.color + ' text-white shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]'
                            : 'bg-white hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[1px] hover:translate-y-[1px]'
                        ]"
                        @click="profileForm.gender = profileForm.gender === g.value ? null : g.value"
                      >
                        {{ g.label }}
                      </button>
                    </div>
                  </div>
                </div>

                <!-- 出生日期 -->
                <div>
                  <label class="block font-black text-base mb-2">出生日期</label>
                  <input
                    v-model="profileForm.birth_date"
                    type="date"
                    class="w-full border-2 border-black bg-white px-4 py-3 font-mono text-base focus:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] focus:outline-none transition-all"
                  />
                </div>

                <!-- 头像颜色选择器 -->
                <div>
                  <label class="block font-black text-base mb-2">头像颜色</label>
                  <div class="flex gap-3 flex-wrap">
                    <button
                      v-for="color in avatarColors"
                      :key="color"
                      type="button"
                      class="w-12 h-12 border-2 border-black transition-all duration-200 hover:scale-110"
                      :class="previewColor === color || (!previewColor && user?.avatar_color === color) ? 'shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] scale-110' : ''"
                      :style="{ backgroundColor: color }"
                      @click="previewColor = color; profileForm.avatar_color = color"
                    />
                  </div>
                </div>

                <!-- 反馈消息 -->
                <div
                  v-if="profileMessage"
                  :class="[
                    'font-mono text-base p-4 border-2',
                    profileSuccess ? 'bg-memphis-teal/10 border-memphis-teal' : 'bg-memphis-coral/10 border-memphis-coral text-memphis-coral'
                  ]"
                >
                  {{ profileMessage }}
                </div>

                <!-- 保存按钮 -->
                <button
                  type="submit"
                  :disabled="profileSaving"
                  class="w-full bg-memphis-coral text-white font-black py-3.5 border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:shadow-[1px_1px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200 text-base disabled:cursor-not-allowed"
                >
                  {{ profileSaving ? '保存中...' : '💾 保存资料' }}
                </button>
              </form>
            </div>
          </div>
        </div>

      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useAuthStore, type ProfileUpdate } from '@/stores/auth'
import { useCareerStore, type AssessmentRecord } from '@/stores/career'

const authStore = useAuthStore()
const careerStore = useCareerStore()
const user = computed(() => authStore.user)

// ── 职业测评数据 ────────────────────────────────────────
const hollandRecord = ref<AssessmentRecord | null>(null)
const mbtiRecord = ref<AssessmentRecord | null>(null)
const cvRecord = ref<AssessmentRecord | null>(null)

const hasAssessmentResults = computed(() => !!(hollandRecord.value || mbtiRecord.value || cvRecord.value))

// Holland 解析
const hResult = computed(() => hollandRecord.value?.result as Record<string, unknown> | undefined)
const hollandCode = computed(() => (hResult.value?.holland_code as string) || '')
const hollandTop3 = computed(() =>
  ((hResult.value?.top3 || []) as Array<{ code: string; name: string; desc: string; score: number; careers: string[] }>))

// MBTI 解析
const mbtiResult = computed(() => mbtiRecord.value?.result as Record<string, unknown> | undefined)
const mbtiType = computed(() => (mbtiResult.value?.type as string) || '')
const mbtiInfo = computed(() => mbtiResult.value?.type_info as Record<string, unknown> | undefined)

// 职业价值观解析
const cvResult = computed(() => cvRecord.value?.result as Record<string, unknown> | undefined)
const cvCoreNames = computed(() => {
  const dims = ((cvResult.value?.dimensions || []) as Array<{ name: string; is_core: boolean }>)
  return dims.filter(d => d.is_core).map(d => d.name).join(' 与 ')
})

const todayStr = computed(() => new Date().toLocaleDateString('zh-CN'))

// 从测评历史中加载最新的各类型测评结果
async function loadLatestAssessments() {
  try {
    await careerStore.fetchHistory()
    const items = careerStore.history.items
    // 取每种类型最新的一条
    for (const item of items) {
      if (item.type === 'holland' && !hollandRecord.value) hollandRecord.value = item
      if (item.type === 'mbti' && !mbtiRecord.value) mbtiRecord.value = item
      if (item.type === 'career_values' && !cvRecord.value) cvRecord.value = item
      if (hollandRecord.value && mbtiRecord.value && cvRecord.value) break
    }
  } catch {
    // 忽略错误，简历仍然可以导出
  }
}

// ── 导出 PDF ──────────────────────────────────────────────
const exporting = ref(false)

async function handleExportPdf() {
  exporting.value = true
  await nextTick() // 确保打印区域已渲染

  const printEl = document.getElementById('resume-print')
  if (!printEl) { exporting.value = false; return }

  // 显示打印区域
  printEl.style.display = 'block'
  await nextTick()

  // 触发浏览器打印（用户可选择保存为PDF）
  window.print()

  // 打印结束后隐藏
  printEl.style.display = 'none'
  exporting.value = false
}

const avatarText = computed(() => {
  const name = user.value?.nickname || user.value?.username || '用'
  return name.charAt(0).toUpperCase()
})

function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return '未知'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

function genderLabel(g: string | null | undefined): string {
  if (g === 'male') return '男'
  if (g === 'female') return '女'
  if (g === 'other') return '其他'
  return '未设置'
}

// ── 个人资料编辑 ──────────────────────────────────────────

const profileForm = reactive<ProfileUpdate>({
  nickname: null,
  avatar_color: null,
  bio: null,
  phone: null,
  gender: null,
  birth_date: null,
})

const previewColor = ref<string | null>(null)
const profileSaving = ref(false)
const profileMessage = ref('')
const profileSuccess = ref(false)

// ── 头像上传 ──────────────────────────────────────────

const avatarInput = ref<HTMLInputElement | null>(null)
const avatarPreview = ref<string | null>(null)
const avatarUploading = ref(false)

function triggerAvatarUpload() {
  avatarInput.value?.click()
}

async function handleAvatarUpload(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  // 本地预览
  avatarPreview.value = URL.createObjectURL(file)

  // 上传
  avatarUploading.value = true
  const result = await authStore.uploadAvatar(file)
  avatarUploading.value = false

  if (!result.success) {
    avatarPreview.value = null
    profileMessage.value = result.message
    profileSuccess.value = false
  }

  // 清除 input 以允许重新选择同一文件
  input.value = ''
}

const avatarColors = [
  '#ff006e', // coral
  '#ffbe0b', // yellow
  '#00f5d4', // teal
  '#3a86ff', // blue
  '#8338ec', // purple
  '#fb5607', // orange
  '#000000', // black
  '#22c55e', // green
]

const genderOptions = [
  { value: 'male', label: '男', color: 'bg-memphis-blue' },
  { value: 'female', label: '女', color: 'bg-memphis-coral' },
  { value: 'other', label: '其他', color: 'bg-memphis-purple' },
]

function loadProfileToForm() {
  const u = user.value
  if (!u) return
  profileForm.nickname = u.nickname
  profileForm.avatar_color = u.avatar_color
  profileForm.bio = u.bio
  profileForm.phone = u.phone
  profileForm.gender = u.gender
  profileForm.birth_date = u.birth_date
  previewColor.value = u.avatar_color
}

async function handleSaveProfile() {
  profileSaving.value = true
  profileMessage.value = ''
  profileSuccess.value = false

  const result = await authStore.updateProfile(profileForm)
  profileSaving.value = false
  profileMessage.value = result.message
  profileSuccess.value = result.success
}

// ── 初始化 ──────────────────────────────────────────────

onMounted(async () => {
  await authStore.fetchProfile()
  loadProfileToForm()
  await loadLatestAssessments()
})
</script>

<style scoped>
/* 打印区域：默认隐藏，只在打印时显示 */
.resume-print-root {
  display: none;
  position: fixed;
  top: 0; left: 0;
  width: 210mm;
  z-index: -1;
  background: #fff;
}
.resume-page {
  padding: 18mm 20mm;
  font-family: 'Microsoft YaHei', 'PingFang SC', 'Helvetica Neue', sans-serif;
  color: #1a1a1a;
  line-height: 1.5;
}
.resume-header {
  display: flex; gap: 20px; align-items: flex-start;
}
.resume-avatar {
  width: 88px; height: 88px; border: 2px solid #000; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center; overflow: hidden;
}
.resume-avatar-letter { font-size: 38px; font-weight: 900; color: #fff; }
.resume-header-info { flex: 1; }
.resume-name { font-size: 26px; font-weight: 900; margin: 0 0 6px 0; letter-spacing: 2px; }
.resume-meta { display: flex; flex-wrap: wrap; gap: 14px; font-size: 12px; color: #444; margin-bottom: 8px; }
.resume-target { display: flex; align-items: center; gap: 8px; margin-top: 4px; }
.resume-target-label {
  font-size: 11px; font-weight: 700; padding: 2px 8px;
  background: #1a1a1a; color: #fff; letter-spacing: 1px;
}
.resume-target-value { font-size: 14px; font-weight: 900; color: #ff006e; }
.resume-divider { height: 2px; background: #000; margin: 16px 0; }
.resume-section { margin-bottom: 14px; }
.resume-section-title {
  font-size: 14px; font-weight: 900; margin: 0 0 8px 0;
  padding-bottom: 3px; border-bottom: 1.5px solid #000; letter-spacing: 2px;
}
.resume-text { font-size: 12px; margin: 0; white-space: pre-wrap; }
.resume-exp { }
.resume-exp-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px; }
.resume-exp-company { font-size: 13px; font-weight: 700; }
.resume-exp-date { font-size: 11px; color: #555; }
.resume-exp-role { font-size: 12px; font-weight: 700; color: #ff006e; margin-bottom: 4px; }
.resume-exp-list { font-size: 12px; margin: 0; padding-left: 16px; }
.resume-exp-list li { margin-bottom: 3px; }

/* 测评结果 */
.resume-assess-block { margin-bottom: 12px; padding: 10px; background: #fafafa; border: 1px solid #ddd; }
.resume-assess-title { font-size: 12px; font-weight: 900; margin-bottom: 6px; color: #8338ec; }
.resume-assess-result { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin-bottom: 6px; }
.resume-assess-label { font-size: 11px; color: #666; }
.resume-assess-value { font-size: 13px; font-weight: 900; color: #ff006e; }
.resume-assess-sub { font-size: 11px; color: #555; }
.resume-mbti-type { font-size: 18px; letter-spacing: 2px; }
.resume-assess-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }
.resume-tag {
  font-size: 10px; font-weight: 700; padding: 2px 6px;
  border: 1px solid #000; background: #ffbe0b;
}
.resume-assess-summary { font-size: 11px; color: #444; margin: 0; line-height: 1.4; }

.resume-footer { text-align: center; font-size: 10px; color: #999; margin-top: 20px; padding-top: 10px; border-top: 1px solid #ddd; }

/* 打印样式 */
@media print {
  body * { visibility: hidden !important; }
  #resume-print, #resume-print * { visibility: visible !important; }
  #resume-print {
    display: block !important;
    position: fixed !important;
    top: 0 !important; left: 0 !important;
    width: 210mm !important;
    z-index: 99999 !important;
    background: #fff !important;
  }
  @page {
    size: A4;
    margin: 0;
  }
}
</style>
