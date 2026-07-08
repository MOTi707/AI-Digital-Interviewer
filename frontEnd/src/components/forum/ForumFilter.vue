<template>
  <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-4 space-y-2.5 flex flex-col h-full min-h-0">
    <div class="flex items-center justify-between shrink-0">
      <h3 class="font-black text-base tracking-tight">🔍 筛选</h3>
      <button
        class="font-mono text-xs px-2 py-1 border-2 border-black bg-memphis-cream hover:bg-memphis-yellow transition-colors"
        @click="$emit('reset')"
      >
        重置
      </button>
    </div>

    <!-- 搜索关键词 -->
    <div class="shrink-0">
      <label class="font-black text-xs block mb-1.5">关键词</label>
      <input
        v-model="localKeyword"
        class="w-full border-4 border-black bg-white px-3 py-1.5 font-mono text-xs focus:shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] focus:outline-none transition-all"
        placeholder="搜索标题/内容..."
        @keyup.enter="$emit('search', localKeyword)"
      />
    </div>

    <!-- 公司 -->
    <FilterSelect
      label="公司"
      :options="options?.companies || []"
      :model-value="filters.company"
      @update:model-value="(v: string | null) => $emit('update-filter', 'company', v)"
    />

    <!-- 岗位 -->
    <FilterSelect
      label="岗位"
      :options="options?.positions || []"
      :model-value="filters.position"
      @update:model-value="(v: string | null) => $emit('update-filter', 'position', v)"
    />

    <!-- 年份 -->
    <FilterSelect
      label="年份"
      :options="(options?.years || []).map(String)"
      :model-value="filters.year ? String(filters.year) : null"
      @update:model-value="(v: string | null) => $emit('update-filter', 'year', v ? Number(v) : null)"
    />

    <!-- 状态 -->
    <div class="shrink-0">
      <label class="font-black text-xs block mb-1.5">状态</label>
      <div
        class="flex flex-wrap gap-1.5 overflow-hidden transition-all duration-300"
        :class="statusExpanded ? 'max-h-96' : 'max-h-[62px]'"
      >
        <button
          v-for="s in statusList"
          :key="s.value"
          :class="[
            'font-mono text-xs px-2 py-1 border-2 border-black transition-all duration-200',
            filters.status === s.value
              ? s.activeClass + ' text-white'
              : 'bg-white hover:bg-memphis-cream'
          ]"
          @click="$emit('update-filter', 'status', filters.status === s.value ? null : s.value)"
        >
          {{ s.label }}
        </button>
      </div>
      <button
        v-if="statusList.length > 6"
        class="font-mono text-xs text-memphis-coral mt-3 hover:underline transition-all"
        @click="statusExpanded = !statusExpanded"
      >
        {{ statusExpanded ? '收起 ▲' : '更多 ▼' }}
      </button>
    </div>

    <!-- 面试类型 -->
    <div class="shrink-0">
      <label class="font-black text-xs block mb-1.5">面试类型</label>
      <div class="flex gap-1.5">
        <button
          v-for="t in ['远程', '线下']"
          :key="t"
          :class="[
            'font-mono text-xs px-2 py-1 border-2 border-black transition-all duration-200',
            filters.interview_type === t
              ? 'bg-memphis-blue text-white'
              : 'bg-white hover:bg-memphis-cream'
          ]"
          @click="$emit('update-filter', 'interview_type', filters.interview_type === t ? null : t)"
        >
          {{ t }}
        </button>
      </div>
    </div>

    <!-- 技术标签（弹性区域，吸收剩余空间） -->
    <div class="flex-1 flex flex-col min-h-0">
      <label class="font-black text-xs block mb-1.5 shrink-0">技术标签</label>
      <div class="flex-1 overflow-y-auto min-h-0">
        <div class="flex flex-wrap gap-1.5">
        <button
          v-for="tag in tagStats"
          :key="tag.name"
          :class="[
            'font-mono text-xs px-2 py-1 border-2 border-black transition-all duration-200',
            filters.tags.includes(tag.name)
              ? 'bg-memphis-yellow'
              : 'bg-white hover:bg-memphis-cream'
          ]"
          @click="toggleTag(tag.name)"
        >
          {{ tag.name }} ({{ tag.count }})
        </button>
        </div>
      </div>
    </div>

    <!-- 排序 -->
    <div class="shrink-0">
      <label class="font-black text-xs block mb-1.5">排序</label>
      <div class="flex gap-1.5">
        <button
          v-for="s in sortOptions"
          :key="s.value"
          :class="[
            'flex-1 font-mono text-xs px-2 py-1.5 border-2 border-black transition-all duration-200',
            filters.sort_by === s.value
              ? 'bg-memphis-purple text-white'
              : 'bg-white hover:bg-memphis-cream'
          ]"
          @click="$emit('update-sort', s.value)"
        >
          {{ s.label }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { FilterOptions, PostFilters, TagStat } from '@/stores/forum'
import FilterSelect from './FilterSelect.vue'

const props = defineProps<{
  filters: PostFilters
  options: FilterOptions | null
  tagStats: TagStat[]
}>()

const emit = defineEmits<{
  'update-filter': [key: string, value: any]
  'update-sort': [value: 'latest' | 'hottest']
  'search': [keyword: string]
  'reset': []
}>()

const localKeyword = ref(props.filters.keyword)
const statusExpanded = ref(false)

const statusList = [
  { value: 'offer', label: '录用', activeClass: 'bg-memphis-purple' },
  { value: 'waitlist', label: '备胎', activeClass: 'bg-memphis-yellow' },
  { value: 'rejected', label: '感谢信', activeClass: 'bg-memphis-coral' },
  { value: 'in_progress', label: '流程中', activeClass: 'bg-memphis-blue' },
]

const sortOptions: { value: 'latest' | 'hottest'; label: string }[] = [
  { value: 'latest', label: '🕐 最新' },
  { value: 'hottest', label: '🔥 最热' },
]

function toggleTag(name: string) {
  const tags = [...props.filters.tags]
  const idx = tags.indexOf(name)
  if (idx >= 0) {
    tags.splice(idx, 1)
  } else {
    tags.push(name)
  }
  emit('update-filter', 'tags', tags)
}
</script>
