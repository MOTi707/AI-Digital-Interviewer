<template>
  <div class="h-full p-6 grid grid-cols-12 gap-6">
    <!-- 左侧：筛选面板 -->
    <div class="col-span-3 flex flex-col overflow-hidden min-h-0">
      <ForumFilter
        :filters="forumStore.filters"
        :options="forumStore.filterOptions"
        :tag-stats="forumStore.tagStats"
        @update-filter="handleFilterUpdate"
        @update-sort="handleSortUpdate"
        @search="handleSearch"
        @reset="handleReset"
      />
    </div>

    <!-- 中间：帖子列表 -->
    <div class="col-span-7 flex flex-col gap-5 overflow-hidden">
      <!-- 搜索 + 发帖 -->
      <div class="flex gap-4 shrink-0">
        <input
          v-model="searchInput"
          class="flex-1 border-4 border-black bg-white px-4 py-2.5 font-mono text-sm focus:shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] focus:outline-none transition-all"
          placeholder="搜索面经..."
          @keyup.enter="handleSearch(searchInput)"
        />
        <button
          class="bg-memphis-blue text-white font-black px-6 py-2.5 border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[3px] hover:translate-y-[3px] transition-all duration-200 text-sm shrink-0"
          @click="$emit('create')"
        >
          ✏️ 发布面经
        </button>
      </div>

      <!-- 加载状态 -->
      <div v-if="forumStore.loading" class="flex-1 flex items-center justify-center">
        <div class="font-black text-lg tracking-tight">加载中...</div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="forumStore.posts.length === 0" class="flex-1 flex items-center justify-center">
        <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-8 text-center">
          <div class="text-4xl mb-3">📭</div>
          <div class="font-black text-lg">暂无面经</div>
          <div class="font-mono text-sm text-gray-600 mt-1">试试调整筛选条件或发布第一篇面经</div>
        </div>
      </div>

      <!-- 帖子列表 -->
      <div v-else class="flex-1 space-y-5 overflow-y-auto">
        <div
          v-for="post in forumStore.posts"
          :key="post.id"
          class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-5 hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] hover:-translate-y-0.5 transition-all duration-200 cursor-pointer"
          @click="$emit('detail', post.id)"
        >
          <!-- 标题行 -->
          <div class="flex items-start justify-between gap-3 mb-3">
            <h3 class="font-black text-sm tracking-tight leading-snug line-clamp-2 flex-1">
              {{ post.title }}
            </h3>
            <StatusBadge :status="post.status" />
          </div>

          <!-- 结构化标签 -->
          <div class="flex flex-wrap gap-2 mb-3">
            <span class="font-mono text-xs px-2 py-0.5 border-2 border-black bg-memphis-coral text-white">
              {{ post.company }}
            </span>
            <span class="font-mono text-xs px-2 py-0.5 border-2 border-black bg-memphis-blue text-white">
              {{ post.position }}
            </span>
            <span class="font-mono text-xs px-2 py-0.5 border-2 border-black bg-memphis-purple text-white">
              {{ post.year }}
            </span>
            <span v-if="post.interview_type" class="font-mono text-xs px-2 py-0.5 border-2 border-black bg-memphis-cream">
              {{ post.interview_type }}
            </span>
          </div>

          <!-- 正文摘要 -->
          <p class="font-mono text-xs text-gray-700 mb-3 line-clamp-3">
            {{ post.content }}
          </p>

          <!-- 技术标签 -->
          <div v-if="post.tags.length" class="flex flex-wrap gap-1.5 mb-3">
            <span
              v-for="tag in post.tags"
              :key="tag.name"
              class="font-mono text-xs px-2 py-0.5 border-2 border-black bg-memphis-yellow"
            >
              {{ tag.name }}
            </span>
          </div>

          <!-- 底部信息 -->
          <div class="flex items-center justify-between">
            <div class="font-mono text-xs text-gray-600">
              {{ post.author_name }} · {{ formatDate(post.created_at) }}
            </div>
            <div class="flex items-center gap-3 font-mono text-xs text-gray-600">
              <button
                class="flex items-center gap-1 hover:text-memphis-coral transition-colors"
                :class="{ 'text-memphis-coral': post.is_liked }"
                @click.stop="handleLike(post.id)"
              >
                {{ post.is_liked ? '❤️' : '🤍' }} {{ post.likes_count }}
              </button>
              <span class="flex items-center gap-1">💬 {{ post.comments_count }}</span>
              <button
                class="hover:text-memphis-blue transition-colors"
                @click.stop="handleShare(post.id)"
              >
                🔗
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="forumStore.total > forumStore.size" class="shrink-0 flex items-center justify-center gap-3 pt-2">
        <button
          v-for="p in totalPages"
          :key="p"
          :class="[
            'w-8 h-8 border-2 border-black font-black text-xs transition-all duration-200',
            forumStore.page === p
              ? 'bg-black text-white'
              : 'bg-white hover:bg-memphis-cream'
          ]"
          @click="handlePageChange(p)"
        >
          {{ p }}
        </button>
      </div>
    </div>

    <!-- 右侧：热门标签 -->
    <div class="col-span-2 overflow-hidden">
      <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] p-4">
        <h3 class="font-black text-sm tracking-tight mb-3">🏷️ 热门标签</h3>
        <div
          class="flex flex-wrap gap-2 overflow-hidden transition-all duration-300"
          :class="rightTagsExpanded ? 'max-h-[500px]' : 'max-h-[144px]'"
        >
          <button
            v-for="tag in forumStore.tagStats"
            :key="tag.name"
            class="font-mono text-xs px-2 py-1 border-2 border-black bg-memphis-cream hover:bg-memphis-yellow cursor-pointer transition-colors"
            @click="handleTagClick(tag.name)"
          >
            {{ tag.name }} <span class="text-gray-600 ml-0.5">({{ tag.count }})</span>
          </button>
        </div>
        <button
          v-if="forumStore.tagStats.length > 8"
          class="font-mono text-xs text-memphis-coral mt-3 hover:underline transition-all"
          @click="rightTagsExpanded = !rightTagsExpanded"
        >
          {{ rightTagsExpanded ? '收起 ▲' : '更多 ▼' }}
        </button>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useForumStore } from '@/stores/forum'
import ForumFilter from './ForumFilter.vue'
import StatusBadge from './StatusBadge.vue'

const emit = defineEmits<{
  create: []
  detail: [postId: string]
}>()

const forumStore = useForumStore()
const searchInput = ref('')
const rightTagsExpanded = ref(false)

const totalPages = computed(() => Math.ceil(forumStore.total / forumStore.size))

onMounted(async () => {
  if (!forumStore.filterOptions) {
    await forumStore.fetchFilterOptions()
  }
  if (forumStore.tagStats.length === 0) {
    await forumStore.fetchTagStats()
  }
  if (forumStore.posts.length === 0) {
    await forumStore.fetchPosts()
  }
})

function handleFilterUpdate(key: string, value: any) {
  (forumStore.filters as any)[key] = value
  forumStore.page = 1
  forumStore.fetchPosts()
}

function handleSortUpdate(value: 'latest' | 'hottest') {
  forumStore.filters.sort_by = value
  forumStore.page = 1
  forumStore.fetchPosts()
}

function handleSearch(keyword: string) {
  forumStore.filters.keyword = keyword
  forumStore.page = 1
  forumStore.fetchPosts()
}

function handleReset() {
  forumStore.resetFilters()
  searchInput.value = ''
  forumStore.fetchPosts()
}

function handlePageChange(p: number) {
  forumStore.setPage(p)
  forumStore.fetchPosts()
}

async function handleLike(postId: string) {
  await forumStore.toggleLike(postId)
}

function truncateContent(content: string, maxLen = 100): string {
  return content.length > maxLen ? content.slice(0, maxLen) + '...' : content
}

function handleTagClick(tagName: string) {
  const tags = forumStore.filters.tags.includes(tagName)
    ? forumStore.filters.tags.filter((t) => t !== tagName)
    : [...forumStore.filters.tags, tagName]
  forumStore.filters.tags = tags
  forumStore.page = 1
  forumStore.fetchPosts()
}

async function handleShare(postId: string) {
  const url = `${window.location.origin}/forum/post/${postId}`
  try {
    await navigator.clipboard.writeText(url)
    alert('链接已复制到剪贴板')
  } catch {
    alert('复制失败，请手动复制链接')
  }
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}
</script>
