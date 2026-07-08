<template>
  <div class="h-screen w-screen overflow-y-auto bg-[#fef9ef]">
    <!-- 顶部导航 -->
    <nav class="sticky top-0 z-50 bg-white border-b-4 border-black px-6 py-3 flex items-center justify-between">
      <router-link to="/dashboard" class="font-black text-lg tracking-tight flex items-center gap-2">
        <span class="inline-block w-7 h-7 bg-[#ff006e] border-2 border-black" />
        <span>AI面试官</span>
      </router-link>
      <div class="flex gap-3">
        <router-link
          to="/interview/history"
          class="border-4 border-black bg-white px-4 py-1.5 font-black text-xs shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all duration-200"
        >
          📋 面试历史
        </router-link>
        <router-link
          to="/dashboard"
          class="border-4 border-black bg-[#fef9ef] px-4 py-1.5 font-black text-xs shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all duration-200"
        >
          ← 返回仪表盘
        </router-link>
      </div>
    </nav>

    <!-- 主内容 -->
    <div class="max-w-6xl mx-auto px-6 py-8">
      <!-- 标题区域 -->
      <div class="mb-8">
        <h1 class="font-black text-3xl md:text-4xl tracking-tight mb-2">模拟面试</h1>
        <p class="font-sans text-sm md:text-base text-gray-700">选择目标岗位，开启全真模拟面试之旅</p>
      </div>

      <!-- 面试流程说明 -->
      <div class="border-4 border-black bg-white shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-5 mb-8">
        <h2 class="font-black text-lg mb-3">面试流程</h2>
        <div class="flex flex-wrap gap-2 items-center">
          <div
            v-for="(step, idx) in steps"
            :key="step.key"
            class="flex items-center gap-2"
          >
            <div class="border-2 border-black px-3 py-1 font-black text-xs" :class="step.bg">
              {{ step.label }}
            </div>
            <span v-if="idx < steps.length - 1" class="text-black font-black">→</span>
          </div>
        </div>
      </div>

      <!-- 岗位选择区域 -->
      <div class="flex gap-6">
        <!-- 左侧分类 -->
        <div class="w-48 shrink-0">
          <div class="sticky top-24 space-y-2">
            <button
              v-for="cat in store.jobCategories"
              :key="cat.category"
              :class="[
                'w-full text-left border-4 border-black px-4 py-3 font-black text-sm transition-all duration-200',
                activeCategory === cat.category
                  ? 'bg-[#ff006e] text-white shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]'
                  : 'bg-white hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px]'
              ]"
              @click="activeCategory = cat.category"
            >
              {{ cat.category }}
            </button>
          </div>
        </div>

        <!-- 右侧岗位网格 -->
        <div class="flex-1">
          <div v-if="activePositions.length > 0" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            <button
              v-for="pos in activePositions"
              :key="pos.id"
              class="border-4 border-black bg-white shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-5 text-left hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[3px] hover:translate-y-[3px] transition-all duration-200 group"
              @click="handleSelectPosition(pos)"
            >
              <div class="text-3xl mb-2">{{ pos.icon }}</div>
              <div class="font-black text-sm">{{ pos.title }}</div>
              <div class="mt-2 text-xs font-sans text-gray-600 opacity-0 group-hover:opacity-100 transition-opacity">
                点击开始面试 →
              </div>
            </button>
          </div>
          <div v-else class="border-4 border-black bg-white p-8 text-center font-sans text-gray-500">
            请选择左侧分类查看岗位
          </div>
        </div>
      </div>
    </div>

    <!-- 确认弹窗 -->
    <Teleport to="body">
      <Transition name="modal-fade">
      <div v-if="showConfirm" class="fixed inset-0 bg-black/60 z-[100] flex items-center justify-center" @click.self="showConfirm = false">
        <div class="border-4 border-black bg-[#fef9ef] shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] p-8 max-w-md w-full mx-4">
          <h3 class="font-black text-xl mb-4">确认开始面试</h3>
          <p class="font-sans text-sm mb-2">目标岗位：<span class="font-black">{{ selectedPos?.title }}</span></p>
          <p class="font-sans text-sm mb-1">行业分类：{{ activeCategory }}</p>
          <p class="font-sans text-xs text-gray-600 mt-3 mb-6">
            面试全程约需30-60分钟，进入后将强制全屏，请确保网络稳定、环境安静。
          </p>
          <div class="flex gap-3">
            <button
              class="flex-1 border-4 border-black bg-[#ff006e] text-white font-black px-4 py-2 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all duration-200"
              @click="confirmStart"
            >
              开始面试
            </button>
            <button
              class="flex-1 border-4 border-black bg-white font-black px-4 py-2 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all duration-200"
              @click="showConfirm = false"
            >
              取消
            </button>
          </div>
        </div>
      </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useInterviewStore, type JobPosition } from '@/stores/interview'

const router = useRouter()
const store = useInterviewStore()

const activeCategory = ref('互联网')
const showConfirm = ref(false)
const selectedPos = ref<JobPosition | null>(null)

const steps = [
  { key: 'assessment', label: '综合素质测评', bg: 'bg-[#3a86ff]' },
  { key: 'tech', label: '一面·技术', bg: 'bg-[#ff006e]' },
  { key: 'business', label: '二面·业务', bg: 'bg-[#ffbe0b]' },
  { key: 'ai_voice_3', label: '三面·AI面试', bg: 'bg-[#8338ec]' },
  { key: 'ai_voice_4', label: '四面·综合面试', bg: 'bg-[#22c55e]' },
]

const activePositions = computed(() => {
  const cat = store.jobCategories.find(c => c.category === activeCategory.value)
  return cat?.positions || []
})

function handleSelectPosition(pos: JobPosition) {
  selectedPos.value = pos
  showConfirm.value = true
}

async function confirmStart() {
  if (!selectedPos.value) return
  showConfirm.value = false
  try {
    const session = await store.startInterview(activeCategory.value, selectedPos.value.title)
    router.push(`/interview/session/${session.id}`)
  } catch (e) {
    alert(`创建面试失败: ${(e as Error).message}`)
  }
}

onMounted(async () => {
  await store.fetchJobs()
})
</script>
