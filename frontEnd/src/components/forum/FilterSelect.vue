<template>
  <div class="shrink-0">
    <label class="font-black text-xs block mb-1.5">{{ label }}</label>
    <select
      :value="modelValue"
      class="w-full border-4 border-black bg-white px-2 py-1.5 font-mono text-xs focus:shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] focus:outline-none transition-all"
      @change="$emit('update:modelValue', ($event.target as HTMLSelectElement).value || null)"
    >
      <option value="">全部</option>
      <option v-for="opt in options" :key="opt" :value="opt">{{ opt }}</option>
    </select>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  options: string[]
  modelValue: string | null
}>()

defineEmits<{
  'update:modelValue': [value: string | null]
}>()
</script>
