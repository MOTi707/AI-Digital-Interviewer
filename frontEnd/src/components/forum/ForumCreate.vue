<template>
  <div class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="$emit('close')">
    <div class="bg-memphis-cream border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] w-full max-w-2xl max-h-[90vh] overflow-y-auto">
      <!-- 标题栏 -->
      <div class="sticky top-0 bg-memphis-cream border-b-4 border-black p-5 flex items-center justify-between z-10">
        <h2 class="font-black text-xl tracking-tight">✏️ 发布面经</h2>
        <button
          class="w-8 h-8 border-2 border-black bg-memphis-coral text-white font-black flex items-center justify-center hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200"
          @click="$emit('close')"
        >
          ✕
        </button>
      </div>

      <form class="p-6 space-y-6" @submit.prevent="handleSubmit">
        <!-- 匿名开关 -->
        <div class="flex items-center gap-4">
          <button
            type="button"
            :class="[
              'px-4 py-2 border-4 border-black font-black text-sm transition-all duration-200',
              form.is_anonymous
                ? 'bg-memphis-purple text-white shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]'
                : 'bg-white hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px]'
            ]"
            @click="form.is_anonymous = !form.is_anonymous"
          >
            {{ form.is_anonymous ? '🕶️ 匿名发布' : '👤 公开身份' }}
          </button>
          <span class="font-mono text-xs text-gray-600">
            {{ form.is_anonymous ? '其他用户看不到你的用户名' : '将显示你的用户名' }}
          </span>
        </div>

        <!-- 标题 -->
        <div>
          <label class="font-black text-sm block mb-2">面经标题 <span class="text-memphis-coral">*</span></label>
          <input
            v-model="form.title"
            class="w-full border-4 border-black bg-white px-3 py-2.5 font-mono text-sm focus:shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] focus:outline-none transition-all"
            placeholder="例：字节跳动前端一面面经"
            required
          />
        </div>

        <!-- 结构化字段网格 -->
        <div class="grid grid-cols-2 gap-4">
          <!-- 公司 -->
          <div>
            <label class="font-black text-xs block mb-2">公司 <span class="text-memphis-coral">*</span></label>
            <input
              v-model="form.company"
              class="w-full border-4 border-black bg-white px-3 py-2 font-mono text-xs focus:shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] focus:outline-none transition-all"
              placeholder="腾讯 / 字节跳动 / ..."
              required
            />
          </div>

          <!-- 岗位 -->
          <div>
            <label class="font-black text-xs block mb-2">岗位 <span class="text-memphis-coral">*</span></label>
            <input
              v-model="form.position"
              class="w-full border-4 border-black bg-white px-3 py-2 font-mono text-xs focus:shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] focus:outline-none transition-all"
              placeholder="前端开发 / 产品经理 / ..."
              required
            />
          </div>

          <!-- 状态 -->
          <div>
            <label class="font-black text-xs block mb-2">结果状态 <span class="text-memphis-coral">*</span></label>
            <select
              v-model="form.status"
              class="w-full border-4 border-black bg-white px-3 py-2 font-mono text-xs focus:shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] focus:outline-none transition-all"
            >
              <option v-for="s in statusOptions" :key="s.value" :value="s.value">{{ s.label }}</option>
            </select>
          </div>

          <!-- 年份 -->
          <div>
            <label class="font-black text-xs block mb-2">年份 <span class="text-memphis-coral">*</span></label>
            <select
              v-model.number="form.year"
              class="w-full border-4 border-black bg-white px-3 py-2 font-mono text-xs focus:shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] focus:outline-none transition-all"
              required
            >
              <option v-for="y in yearOptions" :key="y" :value="y">{{ y }}</option>
            </select>
          </div>

          <!-- 面试类型 -->
          <div>
            <label class="font-black text-xs block mb-2">面试类型</label>
            <select
              v-model="form.interview_type"
              class="w-full border-4 border-black bg-white px-3 py-2 font-mono text-xs focus:shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] focus:outline-none transition-all"
            >
              <option :value="null">不限</option>
              <option value="远程">远程</option>
              <option value="线下">线下</option>
            </select>
          </div>
        </div>

        <!-- 技术标签 -->
        <div>
          <label class="font-black text-sm block mb-2">技术标签（面试题归类）</label>
          <div class="flex flex-wrap gap-3 mb-3">
            <span
              v-for="(tag, i) in form.tag_names"
              :key="i"
              class="font-mono text-xs px-2 py-1 border-2 border-black bg-memphis-yellow flex items-center gap-1"
            >
              {{ tag }}
              <button type="button" class="hover:text-memphis-coral" @click="removeTag(i)">✕</button>
            </span>
          </div>
          <div class="flex gap-3">
            <input
              v-model="tagInput"
              class="flex-1 border-4 border-black bg-white px-3 py-2 font-mono text-xs focus:shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] focus:outline-none transition-all"
              placeholder="输入标签后回车，如：Vue3、计算机网络"
              @keyup.enter="addTag"
            />
            <button
              type="button"
              class="px-3 py-2 border-4 border-black bg-memphis-cream font-black text-xs hover:bg-memphis-yellow transition-colors"
              @click="addTag"
            >
              添加
            </button>
          </div>
          <div class="flex flex-wrap gap-1.5 mt-3">
            <button
              v-for="tag in suggestedTags"
              :key="tag"
              type="button"
              class="font-mono text-xs px-2 py-0.5 border-2 border-black bg-white hover:bg-memphis-yellow transition-colors"
              @click="addSuggestedTag(tag)"
            >
              + {{ tag }}
            </button>
          </div>
        </div>

        <!-- 正文 -->
        <div>
          <label class="font-black text-sm block mb-2">面经正文 <span class="text-memphis-coral">*</span></label>
          <textarea
            v-model="form.content"
            rows="10"
            class="w-full border-4 border-black bg-white px-3 py-2.5 font-mono text-sm focus:shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] focus:outline-none transition-all resize-y"
            placeholder="请详细描述你的面试经历：&#10;- 面试流程（自我介绍 → 项目介绍 → 技术问答 → ...）&#10;- 遇到的面试题目&#10;- 面试官的风格和态度&#10;- 你的感受和建议"
            required
          ></textarea>
          <div class="font-mono text-xs text-gray-600 mt-2">
            {{ form.content.length }} / 最少 10 字
          </div>
        </div>

        <!-- 错误提示 -->
        <div v-if="errorMsg" class="bg-memphis-coral text-white border-4 border-black p-4 font-mono text-sm">
          ⚠️ {{ errorMsg }}
        </div>

        <!-- 提交按钮 -->
        <div class="flex gap-4 pt-3">
          <button
            type="button"
            class="flex-1 py-3 border-4 border-black bg-white font-black text-sm hover:bg-memphis-cream transition-all duration-200 shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[3px] hover:translate-y-[3px]"
            @click="$emit('close')"
          >
            取消
          </button>
          <button
            type="submit"
            :disabled="submitting"
            class="flex-1 py-3 border-4 border-black bg-memphis-coral text-white font-black text-sm transition-all duration-200 shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[3px] hover:translate-y-[3px] disabled:opacity-60"
          >
            {{ submitting ? '发布中...' : '🚀 发布面经' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useForumStore } from '@/stores/forum'
import type { PostCreateData } from '@/stores/forum'

const emit = defineEmits<{
  close: []
  created: []
}>()

const forumStore = useForumStore()
const submitting = ref(false)
const errorMsg = ref('')
const tagInput = ref('')

const form = reactive({
  title: '',
  content: '',
  company: '',
  position: '',
  year: new Date().getFullYear(),
  interview_type: null as string | null,
  status: 'in_progress',
  is_anonymous: false,
  tag_names: [] as string[],
})

const statusOptions = [
  { value: 'in_progress', label: '流程中' },
  { value: 'offer', label: '录用 (Offer)' },
  { value: 'waitlist', label: '备胎' },
  { value: 'rejected', label: '感谢信' },
]
const yearOptions = Array.from({ length: 7 }, (_, i) => 2026 - i)
const suggestedTags = [
  'Vue3', 'React', 'TypeScript', 'JavaScript', 'CSS',
  '计算机网络', '操作系统', '数据结构', '算法', '数据库',
  'Java', 'Python', 'Go', '系统设计', 'LeetCode',
  'Spring', 'MySQL', 'Redis', 'HTTP', 'Git',
]

function addTag() {
  const tag = tagInput.value.trim()
  if (tag && !form.tag_names.includes(tag)) {
    form.tag_names.push(tag)
    tagInput.value = ''
  }
}

function addSuggestedTag(tag: string) {
  if (!form.tag_names.includes(tag)) {
    form.tag_names.push(tag)
  }
}

function removeTag(index: number) {
  form.tag_names.splice(index, 1)
}

async function handleSubmit() {
  errorMsg.value = ''

  if (!form.title || !form.content || !form.company || !form.position) {
    errorMsg.value = '请填写所有必填字段'
    return
  }
  if (form.content.length < 10) {
    errorMsg.value = '正文至少 10 个字符'
    return
  }

  submitting.value = true
  try {
    const data: PostCreateData = {
      title: form.title,
      content: form.content,
      company: form.company,
      position: form.position,
      year: form.year,
      interview_type: form.interview_type,
      status: form.status,
      is_anonymous: form.is_anonymous,
      tag_names: form.tag_names,
    }

    const result = await forumStore.createPost(data)
    if (result.success) {
      emit('close')
      emit('created')
    } else {
      errorMsg.value = result.message
    }
  } finally {
    submitting.value = false
  }
}
</script>
