<template>
  <DashboardLayout>
    <template #default="{ activeModule }">
      <div class="h-full w-full overflow-hidden">
        <!-- 模拟面试模块 -->
        <div v-if="activeModule === 'interview'" class="h-full overflow-y-auto p-6">
          <!-- 面试流程说明 -->
          <div class="border-4 border-black bg-white shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-4 mb-5">
            <h2 class="font-black text-base mb-2">🎯 面试流程</h2>
            <div class="flex flex-wrap gap-2 items-center">
              <div v-for="(step, idx) in interviewSteps" :key="step.key" class="flex items-center gap-2">
                <div class="border-2 border-black px-3 py-1 font-black text-xs" :class="step.bg">{{ step.label }}</div>
                <span v-if="idx < interviewSteps.length - 1" class="text-black font-black">→</span>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-12 gap-5">
            <!-- 左侧：岗位分类 + 岗位网格 -->
            <div class="col-span-8">
              <div class="flex gap-2 mb-4">
                <button
                  v-for="cat in interviewStore.jobCategories"
                  :key="cat.category"
                  :class="[
                    'px-4 py-2 font-black text-sm border-4 border-black transition-all duration-200',
                    activeInterviewCat === cat.category
                      ? 'bg-memphis-coral text-white shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]'
                      : 'bg-white hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px]'
                  ]"
                  @click="activeInterviewCat = cat.category"
                >
                  {{ cat.category }}
                </button>
              </div>
              <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
                <button
                  v-for="pos in activePositions"
                  :key="pos.id"
                  class="border-4 border-black bg-white shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-5 text-left hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[3px] hover:translate-y-[3px] transition-all duration-200 group flex flex-col gap-1.5"
                  @click="handleSelectPosition(pos)"
                >
                  <div class="text-3xl mb-2">{{ pos.icon }}</div>
                  <div class="font-black text-base leading-tight">{{ pos.title }}</div>
                  <div class="text-xs font-sans leading-snug text-gray-500 mt-2">{{ pos.description }}</div>
                </button>
              </div>
            </div>

            <!-- 右侧：统计 + 历史 -->
            <div class="col-span-4 flex flex-col gap-4">
              <div class="grid grid-cols-2 gap-3">
                <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-3">
                  <div class="font-black text-xl text-memphis-coral">{{ interviewHistoryTotal }}</div>
                  <div class="font-mono text-xs text-gray-700 mt-0.5">总面试</div>
                </div>
                <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-3">
                  <div class="font-black text-xl text-memphis-blue">{{ interviewAvgScore }}</div>
                  <div class="font-mono text-xs text-gray-700 mt-0.5">平均分</div>
                </div>
              </div>
              <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-4 flex-1 flex flex-col min-h-0">
                <div class="flex items-center justify-between mb-3">
                  <h3 class="font-black text-sm">📝 最近面试</h3>
                  <button class="font-mono text-xs text-memphis-coral underline hover:no-underline" @click="router.push('/interview/history')">查看全部</button>
                </div>
                <div class="flex-1 space-y-2 overflow-y-auto">
                  <button
                    v-for="item in recentInterviews"
                    :key="item.id"
                    class="w-full text-left flex items-center justify-between border-2 border-black p-2.5 hover:bg-memphis-cream transition-colors"
                    @click="router.push(`/interview/report/${item.id}`)"
                  >
                    <div>
                      <div class="font-black text-xs flex items-center gap-1.5">
                        {{ item.job_title }}
                        <span
                          class="border-2 border-black px-1.5 py-0.5 font-black text-[9px] leading-none"
                          :class="getModeColor(item)"
                        >{{ getModeLabel(item) }}</span>
                      </div>
                      <div class="font-mono text-[10px] text-gray-500 mt-0.5">{{ formatInterviewDate(item.started_at) }}</div>
                    </div>
                    <div class="flex items-center gap-2">
                      <span v-if="item.grade" class="px-2 py-0.5 border-2 border-black font-black text-[10px]" :class="gradeColor(item.grade)">{{ item.grade }}</span>
                      <span class="font-black text-xs">{{ item.total_score ?? '-' }}/{{ getMaxScore(item) }}分</span>
                    </div>
                  </button>
                  <div v-if="recentInterviews.length === 0" class="text-center py-4 font-mono text-xs text-gray-500">暂无面试记录</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 确认弹窗 -->
          <Teleport to="body">
            <div v-if="showInterviewConfirm" class="fixed inset-0 bg-black/60 z-[100] flex items-center justify-center" @click.self="showInterviewConfirm = false">
              <div class="border-4 border-black bg-memphis-cream shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] p-8 max-w-lg w-full mx-4">
                <!-- Step 1: 岗位信息 + 模式选择 -->
                <template v-if="confirmStep === 'mode'">
                  <h3 class="font-black text-xl mb-3">确认开始面试</h3>
                  <p class="font-mono text-sm mb-1">目标岗位：<span class="font-black">{{ selectedPosition?.title }}</span></p>
                  <p class="font-mono text-sm mb-4">行业分类：{{ activeInterviewCat }}</p>

                  <div class="border-2 border-black bg-white p-3 mb-4">
                    <p class="font-black text-xs text-red-600 mb-1">⚠️ 面试须知</p>
                    <ul class="font-mono text-xs text-gray-700 space-y-1">
                      <li>• 进入后将<span class="font-black text-red-600">强制全屏</span>，无法最小化</li>
                      <li>• <span class="font-black">禁止切换标签页</span>或离开浏览器</li>
                      <li>• 切屏≥5次将<span class="font-black text-red-600">自动中止面试</span></li>
                    </ul>
                  </div>

                  <p class="font-black text-sm mb-3">选择面试模式：</p>
                  <div class="flex gap-3 mb-4">
                    <button
                      :class="['flex-1 border-4 border-black p-4 font-black text-sm transition-all duration-200', interviewMode === 'full' ? 'bg-memphis-coral text-white shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]' : 'bg-white hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px]']"
                      @click="selectMode('full')"
                    >
                      <div class="text-2xl mb-1">🚀</div>
                      <div>全流程面试</div>
                      <div class="text-[10px] font-mono mt-1 opacity-70">5轮完整流程</div>
                    </button>
                    <button
                      :class="['flex-1 border-4 border-black p-4 font-black text-sm transition-all duration-200', interviewMode === 'single' ? 'bg-memphis-blue text-white shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]' : 'bg-white hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px]']"
                      @click="selectMode('single')"
                    >
                      <div class="text-2xl mb-1">🎯</div>
                      <div>单轮练习</div>
                      <div class="text-[10px] font-mono mt-1 opacity-70">选择1个轮次练习</div>
                    </button>
                  </div>

                  <button
                    v-if="interviewMode === 'full'"
                    class="w-full bg-memphis-coral text-white font-black px-4 py-2.5 border-4 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all duration-200"
                    @click="confirmStartInterview"
                  >🚀 开始全流程面试</button>
                  <button
                    v-else
                    class="w-full bg-memphis-blue text-white font-black px-4 py-2.5 border-4 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all duration-200"
                    @click="confirmStep = 'round'"
                  >下一步：选择轮次 →</button>

                  <button class="w-full mt-2 bg-white font-black px-4 py-2 border-4 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all duration-200" @click="showInterviewConfirm = false">取消</button>
                </template>

                <!-- Step 2: 轮次选择 -->
                <template v-else-if="confirmStep === 'round'">
                  <h3 class="font-black text-xl mb-2">选择练习轮次</h3>
                  <p class="font-mono text-xs text-gray-600 mb-4">岗位：{{ selectedPosition?.title }} · 完成后将生成该轮单独报告</p>

                  <div class="grid grid-cols-2 gap-3 mb-4">
                    <button
                      v-for="step in interviewSteps"
                      :key="step.key"
                      :class="['border-4 border-black p-3 text-left transition-all duration-200', selectedRound === step.key ? step.bg + ' text-white shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]' : 'bg-white hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px]']"
                      @click="selectedRound = step.key"
                    >
                      <div class="text-xl mb-1">{{ step.icon }}</div>
                      <div class="font-black text-xs">{{ step.label }}</div>
                    </button>
                  </div>

                  <div class="flex gap-3">
                    <button class="flex-1 bg-white font-black px-4 py-2.5 border-4 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all duration-200" @click="confirmStep = 'mode'">← 返回</button>
                    <button
                      :disabled="!selectedRound"
                      class="flex-1 bg-memphis-blue text-white font-black px-4 py-2.5 border-4 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all duration-200 disabled:opacity-50"
                      @click="confirmStartInterview"
                    >🎯 开始练习</button>
                  </div>
                </template>
              </div>
            </div>
          </Teleport>
        </div>

        <!-- 职业测评模块 -->
        <div v-else-if="activeModule === 'career'" class="h-full p-6 grid grid-cols-12 gap-5">
          <div class="col-span-4 flex flex-col gap-5">
            <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-6 flex-1">
              <div class="flex items-center gap-3 mb-4">
                <div class="w-10 h-10 bg-memphis-yellow border-4 border-black flex items-center justify-center">
                  <span class="text-lg">🧭</span>
                </div>
                <h2 class="font-black text-xl tracking-tight">职业倾向测评</h2>
              </div>
              <p class="font-mono text-sm text-gray-700 mb-5">基于 Holland 六维度模型，AI 深度解读你的职业方向</p>
              <div class="space-y-3">
                <div
                  v-for="test in careerTests"
                  :key="test.name"
                  class="border-2 border-black p-3 hover:bg-memphis-yellow/10 transition-colors cursor-pointer"
                  @click="router.push(`/career/test/${test.route}`)"
                >
                  <div class="flex items-center justify-between">
                    <div>
                      <div class="font-black text-sm">{{ test.name }}</div>
                      <div class="font-mono text-xs text-gray-600 mt-0.5">{{ test.desc }}</div>
                    </div>
                    <div class="font-mono text-xs px-2 py-1 border-2 border-black" :class="test.tagColor">{{ test.tag }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="col-span-8 flex flex-col gap-5">
            <div class="grid grid-cols-3 gap-4">
              <div v-for="stat in careerStats" :key="stat.label" class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-4">
                <div class="font-black text-2xl" :class="stat.color">{{ stat.value }}</div>
                <div class="font-mono text-xs text-gray-700 mt-1">{{ stat.label }}</div>
              </div>
            </div>
            <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-6 flex-1">
              <div class="flex items-center justify-between mb-4">
                <h3 class="font-black text-lg tracking-tight">📊 最近测评结果</h3>
                <button class="font-black text-xs px-3 py-1.5 border-2 border-black bg-memphis-yellow shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200" @click="router.push('/career/history')">查看更多 →</button>
              </div>
              <div class="space-y-3">
                <div v-for="(result, idx) in careerResults" :key="idx" class="flex items-center justify-between border-2 border-black p-3 hover:bg-memphis-cream transition-colors cursor-pointer" @click="result.id && router.push(`/career/result/${result.id}`)">
                  <div class="flex items-center gap-3">
                    <div class="w-8 h-8 flex items-center justify-center border-2 border-black bg-memphis-purple font-black text-xs text-white">
                      {{ idx + 1 }}
                    </div>
                    <div>
                      <div class="font-black text-sm">{{ result.type }}</div>
                      <div class="font-mono text-xs text-gray-600">{{ result.date }}</div>
                    </div>
                  </div>
                  <div class="font-black text-sm" :class="result.color">{{ result.result }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 面经论坛模块 -->
        <div v-else-if="activeModule === 'forum'" class="h-full overflow-hidden">
          <ForumList @create="showCreateModal = true" @detail="openDetail" />
          <ForumCreate v-if="showCreateModal" @close="showCreateModal = false" @created="showCreateModal = false" />
          <ForumDetail v-if="detailPostId" :post-id="detailPostId" @close="detailPostId = null" />
        </div>

        <!-- OJ刷题模块 -->
        <div v-else-if="activeModule === 'oj'" class="h-full px-3 py-3 grid grid-cols-12 gap-3 overflow-hidden">
          <!-- 左侧：题目列表 -->
          <div class="col-span-8 flex flex-col min-h-0">
            <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-4 flex-1 flex flex-col overflow-hidden min-h-0">
              <!-- 筛选栏 -->
              <div class="flex items-center gap-3 mb-3 flex-wrap shrink-0">
                <div class="flex items-center gap-2">
                  <span class="font-black text-sm">难度:</span>
                  <button
                    v-for="d in difficultyOptions"
                    :key="d.value"
                    :class="[
                      'px-3 py-1 font-black text-xs border-2 border-black transition-all duration-200',
                      ojFilters.difficulty === d.value
                        ? `${d.color} text-white shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]`
                        : 'bg-white hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[1px] hover:translate-y-[1px]'
                    ]"
                    @click="toggleDifficulty(d.value)"
                  >
                    {{ d.label }}
                  </button>
                </div>
                <input
                  v-model="ojFilters.keyword"
                  class="border-2 border-black px-3 py-1 font-mono text-xs flex-1 min-w-[120px] focus:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] focus:outline-none transition-all"
                  placeholder="搜索题目..."
                  @keyup.enter="searchProblems"
                />
                <button
                  class="px-3 py-1 font-black text-xs border-2 border-black bg-[#22c55e] text-white shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-none transition-all"
                  @click="searchProblems"
                >
                  🔍 搜索
                </button>
              </div>

              <!-- 题目表格 -->
              <div class="flex-1 flex flex-col min-h-0">
                <table class="w-full h-full">
                  <thead class="sticky top-0 bg-memphis-cream z-10">
                    <tr class="border-b-4 border-black">
                      <th class="font-black text-sm text-left py-3 px-3 w-20">ID</th>
                      <th class="font-black text-sm text-left py-3 px-3">题目</th>
                      <th class="font-black text-sm text-left py-3 px-3 w-20">难度</th>
                      <th class="font-black text-sm text-left py-3 px-3 w-44">标签</th>
                      <th class="font-black text-sm text-center py-3 px-3 w-24">通过率</th>
                      <th class="font-black text-sm text-center py-3 px-3 w-20">状态</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="p in paginatedProblems"
                      :key="p.id"
                      class="border-b-2 border-black hover:bg-memphis-cream/50 cursor-pointer transition-colors"
                      @click="goToProblem(p.id)"
                    >
                      <td class="font-mono text-sm py-3.5 px-3">{{ p.display_id }}</td>
                      <td class="font-black text-base py-3.5 px-3">{{ p.title }}</td>
                      <td class="text-left py-3.5 px-3">
                        <span
                          class="inline-block px-2.5 py-1 font-black text-xs border-2 border-black"
                          :class="difficultyColor(p.difficulty)"
                        >
                          {{ difficultyLabel(p.difficulty) }}
                        </span>
                      </td>
                      <td class="py-3.5 px-3">
                        <div class="flex flex-wrap gap-1.5">
                          <span
                            v-for="tag in p.tags.split(',').filter(Boolean)"
                            :key="tag"
                            class="font-mono text-xs px-2 py-0.5 border border-black bg-white"
                          >
                            {{ tag }}
                          </span>
                        </div>
                      </td>
                      <td class="font-mono text-sm text-center py-3.5 px-3">{{ p.acceptance_rate }}%</td>
                      <td class="text-center py-3.5 px-3">
                        <span v-if="p.user_solved" class="text-[#22c55e] font-black text-lg">✓</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <div v-if="ojProblems.length === 0 && !ojLoading" class="text-center py-8 font-mono text-sm text-gray-600">
                  暂无题目数据
                </div>
              </div>

              <!-- 分页控件 -->
              <div class="shrink-0 flex items-center justify-between pt-3 border-t-2 border-black">
                <span class="font-mono text-xs text-gray-700">共 {{ ojProblems.length }} 题，第 {{ ojPage }}/{{ ojTotalPages }} 页</span>
                <div class="flex items-center gap-1.5">
                  <button
                    class="px-2.5 py-1 font-black text-xs border-2 border-black bg-white shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-none transition-all duration-200 disabled:cursor-not-allowed disabled:bg-gray-200"
                    :disabled="ojPage <= 1"
                    @click="goToOjPage(ojPage - 1)"
                  >
                    ←
                  </button>
                  <button
                    v-for="p in ojTotalPages"
                    :key="p"
                    :class="[
                      'w-8 h-8 font-black text-xs border-2 border-black transition-all duration-200',
                      ojPage === p
                        ? 'bg-memphis-coral text-white shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]'
                        : 'bg-white hover:bg-memphis-cream hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]'
                    ]"
                    @click="goToOjPage(p)"
                  >
                    {{ p }}
                  </button>
                  <button
                    class="px-2.5 py-1 font-black text-xs border-2 border-black bg-white shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-none transition-all duration-200 disabled:cursor-not-allowed disabled:bg-gray-200"
                    :disabled="ojPage >= ojTotalPages"
                    @click="goToOjPage(ojPage + 1)"
                  >
                    →
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 右侧：进度图表 -->
          <div class="col-span-4 overflow-y-auto min-h-0">
            <ProgressChart :progress="ojProgress" />
          </div>
        </div>
      </div>
    </template>
  </DashboardLayout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import DashboardLayout from '@/components/DashboardLayout.vue'
import ForumList from '@/components/forum/ForumList.vue'
import ForumCreate from '@/components/forum/ForumCreate.vue'
import ForumDetail from '@/components/forum/ForumDetail.vue'
import ProgressChart from '@/components/oj/ProgressChart.vue'
import { useOjStore } from '@/stores/oj'
import { useCareerStore } from '@/stores/career'
import { useInterviewStore, type JobPosition } from '@/stores/interview'

const router = useRouter()
const ojStore = useOjStore()
const careerStore = useCareerStore()
const interviewStore = useInterviewStore()

// 面经论坛弹窗状态
const showCreateModal = ref(false)
const detailPostId = ref<string | null>(null)
function openDetail(postId: string) { detailPostId.value = postId }

// ── 模拟面试 ──────────────────────────────────────────
const activeInterviewCat = ref('互联网')
const showInterviewConfirm = ref(false)
const selectedPosition = ref<JobPosition | null>(null)
const interviewMode = ref<'full' | 'single'>('full')
const selectedRound = ref<string | null>(null)
const confirmStep = ref<'mode' | 'round'>('mode')

const interviewStepsMap: Record<string, Array<{ key: string; label: string; icon: string; bg: string }>> = {
  '互联网': [
    { key: 'assessment', label: '综合素质测评', icon: '📝', bg: 'bg-[#3a86ff] text-white' },
    { key: 'tech', label: '一面·技术面试', icon: '💻', bg: 'bg-[#ff006e] text-white' },
    { key: 'business', label: '二面·业务面试', icon: '📊', bg: 'bg-[#ffbe0b]' },
    { key: 'ai_voice_3', label: '三面·AI面试', icon: '🤖', bg: 'bg-[#8338ec] text-white' },
    { key: 'ai_voice_4', label: '四面·企业价值观面试', icon: '🎯', bg: 'bg-[#22c55e] text-white' },
  ],
  '公务员': [
    { key: 'xingce', label: '行政职业能力测验', icon: '📝', bg: 'bg-[#3a86ff] text-white' },
    { key: 'shenlun', label: '申论', icon: '✍️', bg: 'bg-[#ff006e] text-white' },
    { key: 'interview', label: '面试', icon: '🎯', bg: 'bg-[#22c55e] text-white' },
  ],
}

const interviewSteps = computed(() => interviewStepsMap[activeInterviewCat.value] || interviewStepsMap['互联网'])

const activePositions = computed(() => {
  const cat = interviewStore.jobCategories.find(c => c.category === activeInterviewCat.value)
  return cat?.positions || []
})

const interviewHistoryTotal = computed(() => interviewStore.historyItems.length)

const interviewAvgScore = computed(() => {
  const items = interviewStore.historyItems.filter(i => i.total_score !== null)
  if (items.length === 0) return '-'
  const avg = items.reduce((s, i) => s + (i.total_score || 0), 0) / items.length
  return Math.round(avg).toString()
})

const recentInterviews = computed(() => interviewStore.historyItems.slice(0, 5))

function formatInterviewDate(dateStr: string): string {
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function gradeColor(grade: string): string {
  switch (grade) {
    case 'A': return 'bg-[#22c55e] text-white'
    case 'B': return 'bg-[#3a86ff] text-white'
    case 'C': return 'bg-[#ffbe0b]'
    default: return 'bg-[#ff006e] text-white'
  }
}

const roundLabels: Record<string, string> = {
  assessment: '综合素质',
  tech: '技术面',
  business: '业务面',
  ai_voice_3: 'AI面试',
  ai_voice_4: '综合面试',
}

function getModeLabel(item: { interview_mode: string; target_round: string | null }): string {
  if (item.interview_mode === 'full') return '全流程'
  if (item.interview_mode === 'single' && item.target_round) {
    return `单项·${roundLabels[item.target_round] || item.target_round}`
  }
  return '单项'
}

function getModeColor(item: { interview_mode: string }): string {
  return item.interview_mode === 'full' ? 'bg-[#3a86ff] text-white' : 'bg-[#ffbe0b]'
}

const roundMaxScore: Record<string, number> = {
  assessment: 100,
  tech: 20,
  business: 50,
  ai_voice_3: 90,
  ai_voice_4: 90,
}

function getMaxScore(item: { interview_mode: string; target_round: string | null }): number {
  if (item.interview_mode === 'full') return 350
  if (item.target_round && roundMaxScore[item.target_round]) return roundMaxScore[item.target_round]
  return 350
}

function handleSelectPosition(pos: JobPosition) {
  selectedPosition.value = pos
  interviewMode.value = 'full'
  selectedRound.value = null
  confirmStep.value = 'mode'
  showInterviewConfirm.value = true
}

function selectMode(mode: 'full' | 'single') {
  interviewMode.value = mode
}

async function confirmStartInterview() {
  if (!selectedPosition.value) return
  if (interviewMode.value === 'single' && !selectedRound.value) return
  showInterviewConfirm.value = false
  try {
    const session = await interviewStore.startInterview(
      activeInterviewCat.value,
      selectedPosition.value.title,
      interviewMode.value,
      interviewMode.value === 'single' ? selectedRound.value : null
    )
    router.push(`/interview/session/${session.id}`)
  } catch (e) {
    alert(`创建面试失败: ${(e as Error).message}`)
  }
}

// ── OJ 刷题 ──────────────────────────────────────────
const ojProblems = ref(ojStore.problems)
const ojProgress = ref(ojStore.userProgress)
const ojLoading = ref(false)
const ojFilters = reactive({
  difficulty: null as string | null,
  tag: null as string | null,
  keyword: '',
})

const ojPage = ref(1)
const ojPageSize = 8
const ojTotalPages = computed(() => Math.max(1, Math.ceil(ojProblems.value.length / ojPageSize)))
const paginatedProblems = computed(() => {
  const start = (ojPage.value - 1) * ojPageSize
  return ojProblems.value.slice(start, start + ojPageSize)
})
function goToOjPage(p: number) {
  if (p < 1 || p > ojTotalPages.value) return
  ojPage.value = p
}

const difficultyOptions = [
  { value: 'easy', label: '简单', color: 'bg-[#22c55e]' },
  { value: 'medium', label: '中等', color: 'bg-memphis-yellow' },
  { value: 'hard', label: '困难', color: 'bg-memphis-coral' },
]

function difficultyColor(d: string) {
  if (d === 'easy') return 'bg-[#22c55e] text-white'
  if (d === 'medium') return 'bg-memphis-yellow'
  return 'bg-memphis-coral text-white'
}

function difficultyLabel(d: string) {
  if (d === 'easy') return '简单'
  if (d === 'medium') return '中等'
  return '困难'
}

function toggleDifficulty(value: string) {
  ojFilters.difficulty = ojFilters.difficulty === value ? null : value
  searchProblems()
}

async function searchProblems() {
  ojLoading.value = true
  ojStore.filters.difficulty = ojFilters.difficulty
  ojStore.filters.tag = ojFilters.tag
  ojStore.filters.keyword = ojFilters.keyword
  await ojStore.fetchProblems()
  ojProblems.value = ojStore.problems
  ojPage.value = 1
  ojLoading.value = false
}

function goToProblem(problemId: string) {
  router.push(`/oj/problem/${problemId}`)
}

onMounted(async () => {
  await ojStore.fetchProblems()
  ojProblems.value = ojStore.problems
  await ojStore.fetchProgress()
  ojProgress.value = ojStore.userProgress
  await careerStore.fetchHistory()
  await interviewStore.fetchJobs()
  await interviewStore.fetchHistory()
})

// 职业测评
const careerTests = [
  { name: 'Holland 六维度测评', desc: '探索你的职业兴趣类型', tag: '推荐', tagColor: 'bg-memphis-coral text-white', route: 'holland' },
  { name: 'MBTI 性格测试', desc: '了解你的性格与沟通风格', tag: '热门', tagColor: 'bg-memphis-yellow', route: 'mbti' },
  { name: '职业价值观测评', desc: '发现你最看重的工作因素', tag: '新', tagColor: 'bg-memphis-purple text-white', route: 'career_values' },
]

const careerStats = computed(() => {
  const items = careerStore.history.items
  const total = items.length
  const reports = items.length
  const hollandCount = items.filter(i => i.type === 'holland').length
  return [
    { label: '已完成测评', value: String(total), color: 'text-memphis-purple' },
    { label: '测评报告', value: String(reports), color: 'text-memphis-yellow' },
    { label: 'Holland测评', value: String(hollandCount), color: 'text-memphis-blue' },
  ]
})

const typeLabels: Record<string, string> = {
  holland: 'Holland 六维度',
  mbti: 'MBTI 性格测试',
  career_values: '职业价值观',
}

const careerResults = computed(() => {
  return careerStore.history.items.slice(0, 5).map(item => {
    const r = item.result as Record<string, unknown>
    let resultText = '-'
    if (item.type === 'holland') resultText = `代码: ${r.holland_code || '-'}`
    else if (item.type === 'mbti') resultText = String(r.type || '-')
    else if (item.type === 'career_values') {
      const core = (r.core_values || []) as string[]
      const nameMap: Record<string, string> = { achievement: '成就感', reward: '经济报酬', autonomy: '自主性', contribution: '社会贡献', relationship: '人际关系', environment: '工作环境' }
      resultText = core.map((c: string) => nameMap[c] || c).join(' / ')
    }
    const colorMap: Record<string, string> = { holland: 'text-memphis-purple', mbti: 'text-memphis-blue', career_values: 'text-memphis-coral' }
    return {
      id: item.id,
      type: typeLabels[item.type] || item.type,
      date: new Date(item.created_at).toLocaleDateString('zh-CN'),
      result: resultText,
      color: colorMap[item.type] || 'text-black',
    }
  })
})

</script>
