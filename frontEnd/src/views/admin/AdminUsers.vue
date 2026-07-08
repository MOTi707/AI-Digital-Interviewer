<template>
  <div class="p-6 md:p-8 space-y-5">
    <!-- 标题 -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <div class="w-3 h-12 bg-memphis-blue border-2 border-black" />
        <div>
          <h1 class="font-black text-3xl tracking-tight">用户管理</h1>
          <p class="font-mono text-xs text-black/60 mt-1">共 {{ adminStore.usersTotal }} 人</p>
        </div>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="flex items-center gap-3">
      <input
        v-model="adminStore.userFilters.keyword"
        class="memphis-input flex-1 px-4 py-3 font-mono text-sm"
        placeholder="搜索用户名 / 邮箱 / 昵称..."
        @keyup.enter="search"
      />
      <button
        class="memphis-btn-primary px-5 py-3 font-black text-sm bg-memphis-blue text-white"
        @click="search"
      >
        🔍 搜索
      </button>
    </div>

    <!-- 用户表格 -->
    <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-memphis-blue">
            <tr class="border-b-4 border-black">
              <th class="font-black text-sm text-left py-4 px-4 text-white">用户</th>
              <th class="font-black text-sm text-left py-4 px-4 text-white hidden md:table-cell">邮箱</th>
              <th class="font-black text-sm text-center py-4 px-4 text-white hidden md:table-cell">注册时间</th>
              <th class="font-black text-sm text-center py-4 px-4 text-white">状态</th>
              <th class="font-black text-sm text-center py-4 px-4 text-white">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="user in adminStore.users"
              :key="user.id"
              class="border-b-2 border-black hover:bg-memphis-cream transition-colors duration-200"
            >
              <td class="py-4 px-4">
                <div class="flex items-center gap-3">
                  <div
                    class="w-10 h-10 border-4 border-black flex items-center justify-center font-black text-xs text-white shrink-0 shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]"
                    :style="{ backgroundColor: '#ff006e' }"
                  >
                    {{ user.nickname?.charAt(0) || user.username.charAt(0).toUpperCase() }}
                  </div>
                  <div>
                    <div class="font-black text-sm">{{ user.nickname || user.username }}</div>
                    <div class="font-mono text-[10px] text-black/50">@{{ user.username }}</div>
                  </div>
                </div>
              </td>
              <td class="py-4 px-4 font-mono text-xs text-black/70 hidden md:table-cell">
                {{ user.email || '-' }}
              </td>
              <td class="py-4 px-4 font-mono text-xs text-center hidden md:table-cell">
                {{ formatDate(user.created_at) }}
              </td>
              <td class="py-4 px-4 text-center">
                <span
                  :class="[
                    'inline-block px-3 py-1 font-black text-xs border-4 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]',
                    user.is_active
                      ? 'bg-[#22c55e] text-white'
                      : 'bg-black/10 text-black/50'
                  ]"
                >
                  {{ user.is_active ? '正常' : '禁用' }}
                </span>
              </td>
              <td class="py-4 px-4 text-center">
                <div class="flex items-center justify-center gap-2">
                  <button
                    :class="[
                      'memphis-btn-primary px-3 py-1.5 font-black text-xs border-4',
                      user.is_active
                        ? 'bg-memphis-yellow text-black'
                        : 'bg-[#22c55e] text-white'
                    ]"
                    @click="toggleStatus(user)"
                  >
                    {{ user.is_active ? '禁用' : '启用' }}
                  </button>
                  <button
                    class="memphis-btn-primary px-3 py-1.5 font-black text-xs border-4 bg-memphis-coral text-white"
                    @click="handleDelete(user)"
                  >
                    🗑
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="adminStore.users.length === 0 && !adminStore.usersLoading">
              <td colspan="5" class="text-center py-12 font-mono text-sm text-black/50">
                暂无用户数据
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 分页 -->
    <Pagination
      :page="adminStore.userFilters.page"
      :total="adminStore.usersTotal"
      :size="adminStore.userFilters.size"
      @change="goPage"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAdminStore, type AdminUser } from '@/stores/admin'
import Pagination from './Pagination.vue'

const adminStore = useAdminStore()

function search() {
  adminStore.userFilters.page = 1
  adminStore.fetchUsers()
}

function goPage(p: number) {
  adminStore.userFilters.page = p
  adminStore.fetchUsers()
}

async function toggleStatus(user: AdminUser) {
  try {
    await adminStore.toggleUserStatus(user.id, !user.is_active)
  } catch (e) {
    alert(`操作失败: ${(e as Error).message}`)
  }
}

async function handleDelete(user: AdminUser) {
  if (!confirm(`确定删除用户 "${user.username}" 吗？此操作不可撤销。`)) return
  try {
    await adminStore.deleteUser(user.id)
  } catch (e) {
    alert(`删除失败: ${(e as Error).message}`)
  }
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(() => {
  adminStore.fetchUsers()
})
</script>
