<template>
  <div class="space-y-3">
    <!-- 总览统计卡片 -->
    <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-4">
      <h3 class="font-black text-base tracking-tight mb-2">📊 刷题进度</h3>
      <div v-if="progress" class="space-y-3">
        <!-- 总完成度环形图 -->
        <div class="flex items-center gap-4">
          <svg viewBox="0 0 100 100" class="w-16 h-16 shrink-0">
            <circle
              cx="50" cy="50" r="40"
              fill="none"
              stroke="#e5e5e5"
              stroke-width="12"
            />
            <circle
              cx="50" cy="50" r="40"
              fill="none"
              stroke="#22c55e"
              stroke-width="12"
              stroke-linecap="butt"
              :stroke-dasharray="`${ringPercent * 2.51} 251`"
              stroke-dashoffset="0"
              transform="rotate(-90 50 50)"
            />
            <text
              x="50" y="50"
              text-anchor="middle"
              dominant-baseline="central"
              class="font-black"
              font-size="16"
              fill="#000"
            >
              {{ totalProblems > 0 ? Math.round(progress.total_problems_solved / totalProblems * 100) : 0 }}%
            </text>
          </svg>
          <div class="space-y-1">
            <div class="flex items-center gap-2">
              <span class="w-3 h-3 bg-[#22c55e] border border-black inline-block" />
              <span class="font-mono text-sm">已通过 {{ progress.total_problems_solved }}</span>
            </div>
            <div class="flex items-center gap-2">
              <span class="w-3 h-3 bg-memphis-yellow border border-black inline-block" />
              <span class="font-mono text-sm">已尝试 {{ progress.total_problems_attempted - progress.total_problems_solved }}</span>
            </div>
            <div class="flex items-center gap-2">
              <span class="w-3 h-3 bg-gray-200 border border-black inline-block" />
              <span class="font-mono text-sm">未尝试 {{ totalProblems - progress.total_problems_attempted }}</span>
            </div>
          </div>
        </div>

        <!-- 提交统计 -->
        <div class="grid grid-cols-2 gap-2">
          <div class="border-2 border-black p-2 bg-memphis-cream">
            <div class="font-black text-xl text-memphis-coral">{{ progress.total_submissions }}</div>
            <div class="font-mono text-xs text-gray-700">总提交</div>
          </div>
          <div class="border-2 border-black p-2 bg-memphis-cream">
            <div class="font-black text-xl text-[#22c55e]">{{ progress.total_accepted }}</div>
            <div class="font-mono text-xs text-gray-700">通过提交</div>
          </div>
        </div>
      </div>
      <div v-else class="text-center py-4 font-mono text-sm text-gray-600">
        暂无进度数据
      </div>
    </div>

    <!-- 按难度柱状图 -->
    <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-4">
      <h3 class="font-black text-base tracking-tight mb-2">📈 难度分布</h3>
      <div v-if="progress" class="space-y-3">
        <div
          v-for="d in progress.by_difficulty"
          :key="d.difficulty"
          class="space-y-1"
        >
          <div class="flex items-center justify-between">
            <span class="font-black text-sm" :class="diffLabelColor(d.difficulty)">
              {{ diffLabel(d.difficulty) }}
            </span>
            <span class="font-mono text-xs">{{ d.solved }}/{{ d.total_problems }}</span>
          </div>
          <div class="h-4 border-2 border-black bg-gray-100 relative overflow-hidden">
            <div
              class="h-full transition-all duration-500"
              :class="diffBarColor(d.difficulty)"
              :style="{ width: d.total_problems > 0 ? (d.solved / d.total_problems * 100) + '%' : '0%' }"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 按标签统计 -->
    <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-4">
      <h3 class="font-black text-base tracking-tight mb-2">🏷️ 标签进度</h3>
      <div v-if="progress && progress.by_tag.length > 0" class="space-y-1.5 max-h-[150px] overflow-y-auto">
        <div
          v-for="t in progress.by_tag"
          :key="t.tag"
          class="flex items-center justify-between border-2 border-black p-2 hover:bg-memphis-cream transition-colors"
        >
          <span class="font-black text-sm">{{ t.tag }}</span>
          <span class="font-mono text-xs px-2 py-0.5 border border-black bg-white">
            {{ t.solved }}/{{ t.total }}
          </span>
        </div>
      </div>
      <div v-else class="text-center py-3 font-mono text-sm text-gray-600">
        暂无标签数据
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { UserProgress } from '@/stores/oj'

const props = defineProps<{
  progress: UserProgress | null
}>()

const totalProblems = computed(() => {
  if (!props.progress) return 0
  return props.progress.by_difficulty.reduce((sum, d) => sum + d.total_problems, 0)
})

const ringPercent = computed(() => {
  if (!props.progress || totalProblems.value === 0) return 0
  return props.progress.total_problems_solved / totalProblems.value * 100
})

function diffLabel(d: string) {
  if (d === 'easy') return '简单'
  if (d === 'medium') return '中等'
  return '困难'
}

function diffLabelColor(d: string) {
  if (d === 'easy') return 'text-[#22c55e]'
  if (d === 'medium') return 'text-memphis-yellow'
  return 'text-memphis-coral'
}

function diffBarColor(d: string) {
  if (d === 'easy') return 'bg-[#22c55e]'
  if (d === 'medium') return 'bg-memphis-yellow'
  return 'bg-memphis-coral'
}
</script>
