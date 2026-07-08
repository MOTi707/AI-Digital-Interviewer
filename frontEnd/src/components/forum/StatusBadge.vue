<template>
  <span
    :class="[
      'font-mono text-xs px-2 py-0.5 border-2 border-black shrink-0',
      statusConfig[status]?.class || 'bg-memphis-cream'
    ]"
  >
    {{ statusConfig[status]?.label || status }}
  </span>
</template>

<script setup lang="ts">
defineProps<{
  status: string
}>()

const statusConfig: Record<string, { label: string; class: string }> = {
  offer: { label: '录用', class: 'bg-memphis-purple text-white' },
  waitlist: { label: '备胎', class: 'bg-memphis-yellow' },
  rejected: { label: '感谢信', class: 'bg-memphis-coral text-white' },
  in_progress: { label: '流程中', class: 'bg-memphis-blue text-white' },
}
</script>
