<template>
  <div class="border-4 border-black bg-white shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-4">
    <div class="flex items-center gap-1 overflow-x-auto">
      <div
        v-for="(step, idx) in rounds"
        :key="step.round_key"
        class="flex items-center gap-1 shrink-0"
      >
        <!-- 步骤指示器 -->
        <div
          :class="[
            'flex items-center gap-2 px-3 py-1.5 border-2 border-black font-black text-xs transition-all',
            step.status === 'active' ? 'bg-[#ff006e] text-white animate-pulse' :
            step.status === 'completed' ? 'bg-[#22c55e] text-white' :
            'bg-white text-gray-400'
          ]"
        >
          <!-- 序号 -->
          <span class="w-5 h-5 flex items-center justify-center border border-current text-[10px]">
            {{ step.status === 'completed' ? '✓' : idx + 1 }}
          </span>
          <span class="hidden sm:inline">{{ step.label }}</span>
        </div>
        <!-- 连接线 -->
        <div
          v-if="idx < rounds.length - 1"
          :class="[
            'w-6 h-0.5',
            step.status === 'completed' ? 'bg-[#22c55e]' : 'bg-gray-300'
          ]"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { RoundProgress } from '@/stores/interview'

defineProps<{
  rounds: RoundProgress[]
}>()
</script>
