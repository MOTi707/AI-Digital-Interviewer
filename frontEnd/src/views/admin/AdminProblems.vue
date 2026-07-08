<template>
  <div class="p-6 md:p-8 space-y-5">
    <!-- 标题 -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <div class="w-3 h-12 bg-memphis-yellow border-2 border-black" />
        <div>
          <h1 class="font-black text-3xl tracking-tight">题库管理</h1>
          <p class="font-mono text-xs text-black/60 mt-1">共 {{ adminStore.problemsTotal }} 题</p>
        </div>
      </div>
      <button
        class="memphis-btn-primary px-5 py-3 font-black text-sm bg-memphis-coral text-white"
        @click="openCreate"
      >
        ＋ 新建题目
      </button>
    </div>

    <!-- 筛选栏 -->
    <div class="flex items-center gap-3 flex-wrap">
      <input
        v-model="adminStore.problemFilters.keyword"
        class="memphis-input flex-1 min-w-[180px] px-4 py-3 font-mono text-sm"
        placeholder="搜索题目 / ID..."
        @keyup.enter="search"
      />
      <select
        v-model="adminStore.problemFilters.difficulty"
        class="memphis-input px-4 py-3 font-mono text-sm bg-white"
        @change="search"
      >
        <option value="">全部难度</option>
        <option value="easy">简单</option>
        <option value="medium">中等</option>
        <option value="hard">困难</option>
      </select>
      <button
        class="memphis-btn-primary px-5 py-3 font-black text-sm bg-memphis-blue text-white"
        @click="search"
      >
        🔍 搜索
      </button>
    </div>

    <!-- 题目表格 -->
    <div class="bg-white border-4 border-black shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-memphis-yellow">
            <tr class="border-b-4 border-black">
              <th class="font-black text-sm text-left py-4 px-4">ID</th>
              <th class="font-black text-sm text-left py-4 px-4">题目</th>
              <th class="font-black text-sm text-center py-4 px-4 hidden md:table-cell">难度</th>
              <th class="font-black text-sm text-left py-4 px-4 hidden md:table-cell">标签</th>
              <th class="font-black text-sm text-center py-4 px-4 hidden md:table-cell">通过/提交</th>
              <th class="font-black text-sm text-center py-4 px-4">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="p in adminStore.problems"
              :key="p.id"
              class="border-b-2 border-black hover:bg-memphis-cream transition-colors duration-200"
            >
              <td class="py-4 px-4 font-mono text-xs font-black">{{ p.display_id }}</td>
              <td class="py-4 px-4 font-black text-sm">{{ p.title }}</td>
              <td class="py-4 px-4 text-center hidden md:table-cell">
                <span :class="['inline-block px-3 py-1 font-black text-xs border-4 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]', diffClass(p.difficulty)]">
                  {{ diffLabel(p.difficulty) }}
                </span>
              </td>
              <td class="py-4 px-4 hidden md:table-cell">
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="tag in p.tags.split(',').filter(Boolean)"
                    :key="tag"
                    class="font-mono text-[10px] px-2 py-0.5 border-2 border-black bg-memphis-cream"
                  >
                    {{ tag }}
                  </span>
                </div>
              </td>
              <td class="py-4 px-4 text-center font-mono text-xs hidden md:table-cell">
                <span class="font-black">{{ p.accepted_submissions }}</span>
                <span class="text-black/40"> / {{ p.total_submissions }}</span>
              </td>
              <td class="py-4 px-4 text-center">
                <div class="flex items-center justify-center gap-2">
                  <button
                    class="memphis-btn-primary px-3 py-1.5 font-black text-xs border-4 bg-memphis-yellow"
                    @click="openEdit(p)"
                  >
                    编辑
                  </button>
                  <button
                    class="memphis-btn-primary px-3 py-1.5 font-black text-xs border-4 bg-memphis-coral text-white"
                    @click="handleDelete(p)"
                  >
                    🗑
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="adminStore.problems.length === 0 && !adminStore.problemsLoading">
              <td colspan="6" class="text-center py-12 font-mono text-sm text-black/50">
                暂无题目数据
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <Pagination
      :page="adminStore.problemFilters.page"
      :total="adminStore.problemsTotal"
      :size="adminStore.problemFilters.size"
      @change="goPage"
    />

    <!-- 新建/编辑弹窗 -->
    <Teleport to="body">
      <div
        v-if="showModal"
        class="fixed inset-0 bg-black/70 z-[200] flex items-center justify-center p-4"
        @click.self="showModal = false"
      >
        <div class="border-4 border-black bg-memphis-cream shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] w-full max-w-3xl max-h-[90vh] overflow-y-auto">
          <!-- 弹窗标题栏 -->
          <div class="bg-memphis-coral border-b-4 border-black px-6 py-4 flex items-center justify-between sticky top-0 z-10">
            <h2 class="font-black text-xl text-white tracking-tight">{{ isEdit ? '编辑题目' : '新建题目' }}</h2>
            <button
              class="w-8 h-8 border-4 border-black bg-white font-black text-sm flex items-center justify-center hover:bg-memphis-yellow transition-all duration-200"
              @click="showModal = false"
            >✕</button>
          </div>

          <div class="p-6 space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <label class="space-y-1">
                <span class="font-black text-xs">题目 ID *</span>
                <input v-model="form.display_id" class="memphis-input w-full px-3 py-2 font-mono text-sm" placeholder="P001" />
              </label>
              <label class="space-y-1">
                <span class="font-black text-xs">难度 *</span>
                <select v-model="form.difficulty" class="memphis-input w-full px-3 py-2 font-mono text-sm bg-white">
                  <option value="easy">简单</option>
                  <option value="medium">中等</option>
                  <option value="hard">困难</option>
                </select>
              </label>
            </div>

            <label class="space-y-1 block">
              <span class="font-black text-xs">标题 *</span>
              <input v-model="form.title" class="memphis-input w-full px-3 py-2 font-mono text-sm" placeholder="题目标题" />
            </label>

            <label class="space-y-1 block">
              <span class="font-black text-xs">标签（逗号分隔）</span>
              <input v-model="form.tags" class="memphis-input w-full px-3 py-2 font-mono text-sm" placeholder="数组, 哈希表" />
            </label>

            <div class="grid grid-cols-2 gap-4">
              <label class="space-y-1">
                <span class="font-black text-xs">时间限制 (ms)</span>
                <input v-model.number="form.time_limit" type="number" class="memphis-input w-full px-3 py-2 font-mono text-sm" />
              </label>
              <label class="space-y-1">
                <span class="font-black text-xs">内存限制 (MB)</span>
                <input v-model.number="form.memory_limit" type="number" class="memphis-input w-full px-3 py-2 font-mono text-sm" />
              </label>
            </div>

            <label class="space-y-1 block">
              <span class="font-black text-xs">题目描述 *</span>
              <textarea v-model="form.description" rows="4" class="memphis-input w-full px-3 py-2 font-mono text-sm" placeholder="题目描述..." />
            </label>
            <label class="space-y-1 block">
              <span class="font-black text-xs">输入格式 *</span>
              <textarea v-model="form.input_format" rows="2" class="memphis-input w-full px-3 py-2 font-mono text-sm" />
            </label>
            <label class="space-y-1 block">
              <span class="font-black text-xs">输出格式 *</span>
              <textarea v-model="form.output_format" rows="2" class="memphis-input w-full px-3 py-2 font-mono text-sm" />
            </label>
            <label class="space-y-1 block">
              <span class="font-black text-xs">约束条件 *</span>
              <textarea v-model="form.constraints" rows="2" class="memphis-input w-full px-3 py-2 font-mono text-sm" />
            </label>
            <label class="space-y-1 block">
              <span class="font-black text-xs">样例输入 *</span>
              <textarea v-model="form.sample_input" rows="3" class="memphis-input w-full px-3 py-2 font-mono text-sm" />
            </label>
            <label class="space-y-1 block">
              <span class="font-black text-xs">样例输出 *</span>
              <textarea v-model="form.sample_output" rows="3" class="memphis-input w-full px-3 py-2 font-mono text-sm" />
            </label>
            <label class="space-y-1 block">
              <span class="font-black text-xs">提示（可选）</span>
              <textarea v-model="form.hint" rows="2" class="memphis-input w-full px-3 py-2 font-mono text-sm" />
            </label>

            <div class="flex gap-3 pt-2">
              <button
                class="memphis-btn-primary flex-1 bg-memphis-coral text-white px-4 py-3 font-black text-sm"
                :disabled="saving"
                @click="save"
              >
                {{ saving ? '保存中...' : (isEdit ? '保存修改' : '创建题目') }}
              </button>
              <button
                class="memphis-btn-primary flex-1 bg-white px-4 py-3 font-black text-sm"
                @click="showModal = false"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useAdminStore, type AdminProblem } from '@/stores/admin'
import Pagination from './Pagination.vue'

const adminStore = useAdminStore()

const showModal = ref(false)
const isEdit = ref(false)
const editId = ref<string | null>(null)
const saving = ref(false)

const emptyForm = () => ({
  display_id: '',
  title: '',
  description: '',
  input_format: '',
  output_format: '',
  constraints: '',
  sample_input: '',
  sample_output: '',
  hint: '',
  time_limit: 1000,
  memory_limit: 256,
  difficulty: 'easy' as string,
  tags: '',
})

const form = reactive({ ...emptyForm() })

function search() {
  adminStore.problemFilters.page = 1
  adminStore.fetchProblems()
}

function goPage(p: number) {
  adminStore.problemFilters.page = p
  adminStore.fetchProblems()
}

function openCreate() {
  isEdit.value = false
  editId.value = null
  Object.assign(form, emptyForm())
  showModal.value = true
}

function openEdit(p: AdminProblem) {
  isEdit.value = true
  editId.value = p.id
  form.display_id = p.display_id
  form.title = p.title
  form.description = p.description || ''
  form.input_format = p.input_format || ''
  form.output_format = p.output_format || ''
  form.constraints = p.constraints || ''
  form.sample_input = p.sample_input || ''
  form.sample_output = p.sample_output || ''
  form.hint = p.hint || ''
  form.time_limit = p.time_limit ?? 1000
  form.memory_limit = p.memory_limit ?? 256
  form.difficulty = p.difficulty
  form.tags = p.tags
  showModal.value = true
}

async function save() {
  if (!form.display_id || !form.title || !form.description || !form.difficulty) {
    alert('请填写必填字段（ID、标题、描述、难度）')
    return
  }
  saving.value = true
  try {
    const body = { ...form }
    if (isEdit.value && editId.value) {
      await adminStore.updateProblem(editId.value, body as unknown as Record<string, unknown>)
    } else {
      await adminStore.createProblem(body as unknown as Record<string, unknown>)
    }
    showModal.value = false
    adminStore.fetchProblems()
  } catch (e) {
    alert(`保存失败: ${(e as Error).message}`)
  } finally {
    saving.value = false
  }
}

async function handleDelete(p: AdminProblem) {
  if (!confirm(`确定删除题目 "${p.title}" (${p.display_id}) 吗？`)) return
  try {
    await adminStore.deleteProblem(p.id)
  } catch (e) {
    alert(`删除失败: ${(e as Error).message}`)
  }
}

function diffClass(d: string) {
  if (d === 'easy') return 'bg-[#22c55e] text-white'
  if (d === 'medium') return 'bg-memphis-yellow'
  return 'bg-memphis-coral text-white'
}

function diffLabel(d: string) {
  if (d === 'easy') return '简单'
  if (d === 'medium') return '中等'
  return '困难'
}

onMounted(() => {
  adminStore.fetchProblems()
})
</script>
