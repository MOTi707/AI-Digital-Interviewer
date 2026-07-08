<template>
  <div class="flex items-center gap-2">
    <span class="font-black text-xs text-gray-600">{{ label }}</span>
    <span :class="['font-mono text-xs px-2 py-0.5 border-2 border-black text-white', bg]">
      {{ value }}
    </span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  value: string
  bg: string
}>()
</script>
