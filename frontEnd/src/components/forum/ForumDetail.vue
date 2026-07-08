<template>
  <div class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="$emit('close')">
    <div ref="cardRef" class="bg-memphis-cream border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] w-full max-w-3xl max-h-[90vh] overflow-y-auto">
      <!-- 加载状态 -->
      <div v-if="loading" class="p-8 text-center">
        <div class="font-black text-lg">加载中...</div>
      </div>

      <template v-else-if="post">
        <!-- 标题栏 -->
        <div class="sticky top-0 bg-memphis-cream border-b-4 border-black p-5 flex items-center justify-between z-10">
          <h2 class="font-black text-lg tracking-tight truncate flex-1 mr-4">{{ post.title }}</h2>
          <div class="flex items-center gap-2 shrink-0">
            <button
              class="w-8 h-8 border-2 border-black bg-memphis-coral text-white font-black flex items-center justify-center hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200"
              @click="$emit('close')"
            >
              ✕
            </button>
          </div>
        </div>

        <div class="p-6 space-y-6">
          <!-- 作者信息 -->
          <div class="flex items-center gap-4">
            <div class="w-8 h-8 border-2 border-black bg-memphis-purple flex items-center justify-center font-black text-xs text-white">
              {{ post.author_name[0] || '?' }}
            </div>
            <div>
              <div class="font-black text-sm">{{ post.author_name }}</div>
              <div class="font-mono text-xs text-gray-600">{{ formatDateTime(post.created_at) }}</div>
            </div>
            <StatusBadge :status="post.status" class="ml-auto" />
          </div>

          <!-- 结构化信息 + 技术标签 -->
          <div class="bg-white border-4 border-black p-4">
            <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
              <InfoChip label="公司" :value="post.company" bg="bg-memphis-coral" />
              <InfoChip label="岗位" :value="post.position" bg="bg-memphis-blue" />
              <InfoChip label="年份" :value="String(post.year)" bg="bg-memphis-yellow" />
              <InfoChip v-if="post.interview_type" label="类型" :value="post.interview_type" bg="bg-memphis-orange" />
            </div>
            <div v-if="post.tags.length" class="flex flex-wrap gap-2 mt-3 pt-3 border-t-2 border-black">
              <span
                v-for="tag in post.tags"
                :key="tag.name"
                class="font-mono text-xs px-2 py-1 border-2 border-black bg-memphis-yellow"
              >
                {{ tag.name }}
              </span>
            </div>
          </div>

          <!-- 正文 -->
          <div class="bg-white border-4 border-black p-5">
            <div class="font-mono text-sm whitespace-pre-wrap leading-relaxed">{{ post.content }}</div>
          </div>

          <!-- 操作栏（悬浮底部） -->
          <div class="sticky bottom-0 bg-memphis-cream flex items-center gap-5 border-t-4 border-black pt-4 pb-2 z-[5]">
            <button
              :class="[
                'flex items-center gap-1.5 px-4 py-2 border-4 border-black font-black text-sm transition-all duration-200',
                post.is_liked
                  ? 'bg-memphis-coral text-white shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]'
                  : 'bg-white hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px]'
              ]"
              @click="handleLike"
            >
              {{ post.is_liked ? '❤️' : '🤍' }} {{ post.likes_count }}
            </button>
            <span class="font-mono text-sm">💬 {{ post.comments_count }} 条评论</span>
            <button
              class="ml-auto px-4 py-2 border-4 border-black bg-memphis-purple text-white font-black text-sm hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200 disabled:cursor-not-allowed"
              :disabled="isGenerating"
              @click="handleDownloadImage"
            >
              {{ isGenerating ? '⏳ 生成中...' : '📸 保存图片' }}
            </button>
            <button
              class="px-4 py-2 border-4 border-black bg-memphis-blue text-white font-black text-sm hover:shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200"
              @click="handleShare"
            >
              🔗 链接分享
            </button>
          </div>

          <!-- 评论区 -->
          <div class="border-t-4 border-black pt-5">
            <h3 class="font-black text-base tracking-tight mb-4">💬 评论区</h3>

            <!-- 发评论 -->
            <div class="flex gap-3 mb-5">
              <div class="flex-1">
                <textarea
                  v-model="commentInput"
                  rows="2"
                  class="w-full border-4 border-black bg-white px-3 py-2 font-mono text-sm focus:shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] focus:outline-none transition-all resize-y"
                  placeholder="写下你的评论..."
                ></textarea>
              </div>
              <div class="flex flex-col gap-3 shrink-0">
                <button
                  type="button"
                  :class="[
                    'px-3 py-1.5 border-2 border-black font-mono text-xs transition-all duration-200',
                    commentAnonymous
                      ? 'bg-memphis-purple text-white'
                      : 'bg-white hover:bg-memphis-cream'
                  ]"
                  @click="commentAnonymous = !commentAnonymous"
                >
                  {{ commentAnonymous ? '🕶️ 匿名' : '👤 公开' }}
                </button>
                <button
                  class="px-3 py-1.5 border-2 border-black bg-memphis-coral text-white font-black text-xs hover:bg-memphis-orange transition-colors disabled:opacity-60"
                  :disabled="!commentInput.trim() || submittingComment"
                  @click="submitComment"
                >
                  发送
                </button>
              </div>
            </div>

            <!-- 评论列表 -->
            <div class="space-y-4">
              <div v-if="forumStore.comments.length === 0" class="font-mono text-sm text-gray-600 text-center py-4">
                暂无评论，来发表第一条评论吧
              </div>
              <div
                v-for="comment in forumStore.comments"
                :key="comment.id"
                class="bg-white border-2 border-black p-4"
              >
                <div class="flex items-center gap-3 mb-2">
                  <div class="w-6 h-6 border-2 border-black bg-memphis-orange flex items-center justify-center font-black text-xs text-white">
                    {{ comment.author_name[0] || '?' }}
                  </div>
                  <span class="font-black text-xs">{{ comment.author_name }}</span>
                  <span class="font-mono text-xs text-gray-600 ml-auto">{{ formatDateTime(comment.created_at) }}</span>
                </div>
                <div class="font-mono text-sm whitespace-pre-wrap">{{ comment.content }}</div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>

    <!-- Toast -->
    <Teleport to="body">
      <div
        v-if="toastMsg"
        class="fixed bottom-6 left-1/2 -translate-x-1/2 z-[100] bg-black text-white border-4 border-memphis-yellow px-6 py-3 font-black text-sm shadow-[5px_5px_0px_0px_rgba(255,190,11,1)] transition-all"
      >
        {{ toastMsg }}
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { toBlob } from 'html-to-image'
import { useForumStore } from '@/stores/forum'
import type { PostItem } from '@/stores/forum'
import StatusBadge from './StatusBadge.vue'
import InfoChip from './InfoChip.vue'

const props = defineProps<{
  postId: string
}>()

defineEmits<{
  close: []
}>()

const forumStore = useForumStore()
const post = ref<PostItem | null>(null)
const loading = ref(true)
const commentInput = ref('')
const commentAnonymous = ref(false)
const submittingComment = ref(false)
const toastMsg = ref('')
const isGenerating = ref(false)
const cardRef = ref<HTMLElement | null>(null)

onMounted(async () => {
  await loadData()
})

watch(() => props.postId, async () => {
  await loadData()
})

async function loadData() {
  loading.value = true
  try {
    await forumStore.fetchPost(props.postId)
    post.value = forumStore.currentPost
    await forumStore.fetchComments(props.postId)
  } finally {
    loading.value = false
  }
}

async function handleLike() {
  await forumStore.toggleLike(props.postId)
  if (post.value) {
    post.value.is_liked = forumStore.currentPost?.is_liked ?? post.value.is_liked
    post.value.likes_count = forumStore.currentPost?.likes_count ?? post.value.likes_count
  }
}

async function handleShare() {
  const url = `${window.location.origin}/forum/post/${props.postId}`
  try {
    await navigator.clipboard.writeText(url)
    showToast('链接已复制到剪贴板')
  } catch {
    showToast('复制失败，请手动复制链接')
  }
}

async function handleDownloadImage() {
  if (!cardRef.value || isGenerating.value) return
  isGenerating.value = true

  const el = cardRef.value
  const originalMaxHeight = el.style.maxHeight
  const originalOverflow = el.style.overflow

  try {
    el.style.maxHeight = 'none'
    el.style.overflow = 'visible'

    // toBlob 比 toPng 更快（跳过 base64 编码）
    const blob = await toBlob(el, {
      pixelRatio: 2,
      cacheBust: false,
      skipFonts: true,
      backgroundColor: '#ffffff',
    })

    if (!blob) throw new Error('生成图片失败')

    const link = document.createElement('a')
    link.download = `帖子分享_${Date.now()}.png`
    link.href = URL.createObjectURL(blob)
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(link.href)
    showToast('图片已保存')
  } catch (e) {
    console.error('生成图片失败:', e)
    showToast('生成图片失败，请重试')
  } finally {
    el.style.maxHeight = originalMaxHeight
    el.style.overflow = originalOverflow
    isGenerating.value = false
  }
}

async function submitComment() {
  if (!commentInput.value.trim()) return
  submittingComment.value = true
  try {
    const result = await forumStore.createComment(
      props.postId,
      commentInput.value.trim(),
      commentAnonymous.value,
    )
    if (result.success) {
      commentInput.value = ''
      if (post.value) post.value.comments_count++
    } else {
      showToast(result.message)
    }
  } finally {
    submittingComment.value = false
  }
}

function showToast(msg: string) {
  toastMsg.value = msg
  setTimeout(() => { toastMsg.value = '' }, 2500)
}

function formatDateTime(dateStr: string): string {
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}
</script>
