<template>
  <div class="p-6 md:p-8 space-y-5">
    <!-- 标题 -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <div class="w-3 h-12 bg-memphis-purple border-2 border-black" />
        <div>
          <h1 class="font-black text-3xl tracking-tight">帖子管理</h1>
          <p class="font-mono text-xs text-black/60 mt-1">共 {{ adminStore.postsTotal }} 篇</p>
        </div>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="flex items-center gap-3">
      <input
        v-model="adminStore.postFilters.keyword"
        class="memphis-input flex-1 px-4 py-3 font-mono text-sm"
        placeholder="搜索帖子标题 / 作者..."
        @keyup.enter="search"
      />
      <button
        class="memphis-btn-primary px-5 py-3 font-black text-sm bg-memphis-purple text-white"
        @click="search"
      >
        🔍 搜索
      </button>
    </div>

    <!-- 帖子表格 -->
    <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-memphis-purple">
            <tr class="border-b-4 border-black">
              <th class="font-black text-sm text-left py-4 px-4 text-white">帖子</th>
              <th class="font-black text-sm text-left py-4 px-4 text-white hidden md:table-cell">作者</th>
              <th class="font-black text-sm text-center py-4 px-4 text-white hidden md:table-cell">公司/岗位</th>
              <th class="font-black text-sm text-center py-4 px-4 text-white hidden md:table-cell">互动</th>
              <th class="font-black text-sm text-center py-4 px-4 text-white">状态</th>
              <th class="font-black text-sm text-center py-4 px-4 text-white hidden md:table-cell">发布时间</th>
              <th class="font-black text-sm text-center py-4 px-4 text-white">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="post in adminStore.posts"
              :key="post.id"
              class="border-b-2 border-black hover:bg-memphis-cream transition-colors duration-200"
            >
              <td class="py-4 px-4">
                <div class="font-black text-sm">{{ post.title }}</div>
              </td>
              <td class="py-4 px-4 font-mono text-xs hidden md:table-cell">
                {{ post.author_name }}
              </td>
              <td class="py-4 px-4 text-center hidden md:table-cell">
                <div class="font-mono text-xs">{{ post.company || '-' }}</div>
                <div class="font-mono text-[10px] text-black/50">{{ post.position || '-' }}</div>
              </td>
              <td class="py-4 px-4 text-center hidden md:table-cell">
                <div class="flex items-center justify-center gap-2">
                  <span class="inline-block px-2 py-0.5 font-black text-[10px] border-2 border-black bg-memphis-coral text-white">
                    👍 {{ post.likes_count }}
                  </span>
                  <span class="inline-block px-2 py-0.5 font-black text-[10px] border-2 border-black bg-memphis-blue text-white">
                    💬 {{ post.comments_count }}
                  </span>
                </div>
              </td>
              <td class="py-4 px-4 text-center">
                <span
                  :class="[
                    'inline-block px-3 py-1 font-black text-xs border-4 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]',
                    post.status === 'approved'
                      ? 'bg-[#22c55e] text-white'
                      : post.status === 'pending'
                        ? 'bg-memphis-yellow'
                        : 'bg-memphis-coral text-white'
                  ]"
                >
                  {{ post.status === 'approved' ? '已通过' : post.status === 'pending' ? '待审核' : '已拒绝' }}
                </span>
              </td>
              <td class="py-4 px-4 font-mono text-xs text-center hidden md:table-cell">
                {{ formatDate(post.created_at) }}
              </td>
              <td class="py-4 px-4 text-center">
                <button
                  class="memphis-btn-primary px-3 py-1.5 font-black text-xs border-4 bg-memphis-coral text-white"
                  @click="handleDelete(post)"
                >
                  🗑 删除
                </button>
              </td>
            </tr>
            <tr v-if="adminStore.posts.length === 0 && !adminStore.postsLoading">
              <td colspan="7" class="text-center py-12 font-mono text-sm text-black/50">
                暂无帖子数据
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 分页 -->
    <Pagination
      :page="adminStore.postFilters.page"
      :total="adminStore.postsTotal"
      :size="adminStore.postFilters.size"
      @change="goPage"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAdminStore, type AdminPost } from '@/stores/admin'
import Pagination from './Pagination.vue'

const adminStore = useAdminStore()

function search() {
  adminStore.postFilters.page = 1
  adminStore.fetchPosts()
}

function goPage(p: number) {
  adminStore.postFilters.page = p
  adminStore.fetchPosts()
}

async function handleDelete(post: AdminPost) {
  if (!confirm(`确定删除帖子 "${post.title}" 吗？`)) return
  try {
    await adminStore.deletePost(post.id)
  } catch (e) {
    alert(`删除失败: ${(e as Error).message}`)
  }
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(() => {
  adminStore.fetchPosts()
})
</script>
