<template>
  <div v-if="totalPages > 1" class="flex items-center justify-between pt-3">
    <span class="font-mono text-xs text-black/60">
      第 {{ page }} / {{ totalPages }} 页，共 {{ total }} 条
    </span>
    <div class="flex items-center gap-2">
      <button
        class="memphis-btn-primary w-9 h-9 font-black text-xs border-4 bg-white flex items-center justify-center disabled:cursor-not-allowed disabled:bg-black/5 disabled:shadow-none disabled:hover:transform-none"
        :disabled="page <= 1"
        @click="$emit('change', page - 1)"
      >
        ←
      </button>
      <button
        v-for="p in visiblePages"
        :key="p"
        :class="[
          'w-9 h-9 font-black text-xs border-4 border-black transition-all duration-200',
          p === -1
            ? 'border-0 bg-transparent cursor-default'
            : page === p
              ? 'bg-memphis-coral text-white shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]'
              : 'bg-white hover:bg-memphis-cream hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px]'
        ]"
        :disabled="p === -1"
        @click="p !== -1 && $emit('change', p)"
      >
        {{ p === -1 ? '...' : p }}
      </button>
      <button
        class="memphis-btn-primary w-9 h-9 font-black text-xs border-4 bg-white flex items-center justify-center disabled:cursor-not-allowed disabled:bg-black/5 disabled:shadow-none disabled:hover:transform-none"
        :disabled="page >= totalPages"
        @click="$emit('change', page + 1)"
      >
        →
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ page: number; total: number; size: number }>()
defineEmits<{ change: [page: number] }>()

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.size)))

const visiblePages = computed(() => {
  const tp = totalPages.value
  const p = props.page
  if (tp <= 7) {
    return Array.from({ length: tp }, (_, i) => i + 1)
  }
  if (p <= 4) return [1, 2, 3, 4, 5, -1, tp]
  if (p >= tp - 3) return [1, -1, tp - 4, tp - 3, tp - 2, tp - 1, tp]
  return [1, -1, p - 1, p, p + 1, -1, tp]
})
</script>
