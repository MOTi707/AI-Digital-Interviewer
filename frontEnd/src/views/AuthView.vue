<template>
  <div class="min-h-screen bg-memphis-cream flex items-center justify-center px-4 py-12 relative overflow-hidden">
    <!-- Memphis 装饰元素 -->
    <svg class="absolute top-10 left-10 w-20 h-20 hidden md:block" viewBox="0 0 100 100">
      <polygon points="50,2 2,98 98,98" fill="#ff006e" stroke="#000" stroke-width="6" stroke-linejoin="miter" />
    </svg>
    <div class="absolute bottom-20 right-16 w-24 h-24 rounded-full border-4 border-black bg-memphis-teal hidden md:block" />
    <div class="absolute top-1/4 right-20 w-14 h-14 bg-memphis-yellow border-4 border-black hidden md:block" style="transform: rotate(45deg)" />
    <div class="absolute bottom-32 left-24 w-40 h-2 bg-black hidden md:block" />

    <div class="w-full max-w-md relative z-10">
      <!-- Logo -->
      <router-link to="/" class="flex items-center gap-2 mb-8 justify-center">
        <span class="inline-block w-10 h-10 bg-memphis-coral border-4 border-black" />
        <span class="font-black text-2xl tracking-tight">AI面试官</span>
      </router-link>

      <!-- 主卡片 -->
      <div class="bg-white border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] p-6 md:p-10">
        <!-- 标题 -->
        <div class="text-center mb-6">
          <h1 class="font-black text-3xl md:text-4xl tracking-tight mb-2">
            {{ isLogin ? '欢迎回来' : '创建账号' }}
          </h1>
          <p class="font-mono text-sm text-gray-600">
            {{ isLogin ? '登录以继续使用AI面试平台' : '注册以开始你的AI面试之旅' }}
          </p>
        </div>

        <!-- 注册方式切换（仅注册时显示） -->
        <div v-if="!isLogin" class="flex mb-6 border-4 border-black">
          <button
            :class="[
              'flex-1 py-2 md:py-3 font-black text-sm md:text-base transition-all',
              registerMode === 'email'
                ? 'bg-memphis-coral text-white'
                : 'bg-white text-black hover:bg-memphis-cream'
            ]"
            @click="registerMode = 'email'"
          >
            邮箱注册
          </button>
          <button
            :class="[
              'flex-1 py-2 md:py-3 font-black text-sm md:text-base transition-all border-l-4 border-black',
              registerMode === 'username'
                ? 'bg-memphis-blue text-white'
                : 'bg-white text-black hover:bg-memphis-cream'
            ]"
            @click="registerMode = 'username'"
          >
            用户名注册
          </button>
        </div>

        <!-- 表单 -->
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- 登录：账号字段 -->
          <div v-if="isLogin">
            <label class="block font-black text-sm mb-2">邮箱或用户名</label>
            <input
              v-model="form.account"
              type="text"
              placeholder="请输入邮箱或用户名"
              class="w-full memphis-input px-4 py-3 text-sm md:text-base"
              :class="{ 'border-memphis-coral': errors.account }"
            />
            <p v-if="errors.account" class="text-memphis-coral font-mono text-xs mt-1">{{ errors.account }}</p>
          </div>

          <!-- 注册：邮箱模式 -->
          <template v-if="!isLogin && registerMode === 'email'">
            <div>
              <label class="block font-black text-sm mb-2">邮箱地址</label>
              <input
                v-model="form.email"
                type="email"
                placeholder="请输入邮箱地址"
                class="w-full memphis-input px-4 py-3 text-sm md:text-base"
                :class="{ 'border-memphis-coral': errors.email }"
              />
              <p v-if="errors.email" class="text-memphis-coral font-mono text-xs mt-1">{{ errors.email }}</p>
            </div>
          </template>

          <!-- 注册：用户名模式 -->
          <template v-if="!isLogin && registerMode === 'username'">
            <div>
              <label class="block font-black text-sm mb-2">用户名</label>
              <input
                v-model="form.username"
                type="text"
                placeholder="请输入用户名（至少3个字符）"
                class="w-full memphis-input px-4 py-3 text-sm md:text-base"
                :class="{ 'border-memphis-coral': errors.username }"
              />
              <p v-if="errors.username" class="text-memphis-coral font-mono text-xs mt-1">{{ errors.username }}</p>
            </div>
          </template>

          <!-- 密码字段 -->
          <div>
            <label class="block font-black text-sm mb-2">密码</label>
            <div class="relative">
              <input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                :placeholder="isLogin ? '请输入密码' : '请输入密码（至少6位）'"
                class="w-full memphis-input px-4 py-3 pr-20 text-sm md:text-base"
                :class="{ 'border-memphis-coral': errors.password }"
              />
              <!-- 显示/隐藏 + 强度说明 -->
              <div class="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2">
                <button
                  type="button"
                  @click="showPassword = !showPassword"
                  class="font-mono text-xs text-gray-600 hover:text-black transition-colors"
                >
                  {{ showPassword ? '隐藏' : '显示' }}
                </button>
                <!-- 问号徽标（仅注册时显示） -->
                <div
                  v-if="!isLogin"
                  class="relative"
                  @mouseenter="showStrengthTip = true"
                  @mouseleave="showStrengthTip = false"
                >
                  <button
                    type="button"
                    class="w-5 h-5 border-2 border-black bg-memphis-yellow font-black text-xs leading-none flex items-center justify-center hover:bg-memphis-coral hover:text-white transition-colors"
                  >?</button>
                  <!-- Tooltip -->
                  <div
                    v-if="showStrengthTip"
                    class="absolute bottom-full right-0 mb-2 w-56 border-4 border-black bg-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] p-3 z-20"
                  >
                    <p class="font-black text-xs mb-2 text-memphis-coral tracking-tight">密码强度规则</p>
                    <ul class="font-mono text-xs space-y-1 text-black">
                      <li class="flex items-start gap-1">
                        <span class="inline-block w-2 h-2 mt-0.5 bg-memphis-coral border border-black shrink-0" />
                        <span>弱：不足6位或仅1种字符</span>
                      </li>
                      <li class="flex items-start gap-1">
                        <span class="inline-block w-2 h-2 mt-0.5 bg-memphis-yellow border border-black shrink-0" />
                        <span>中：≥6位且含2种字符类型</span>
                      </li>
                      <li class="flex items-start gap-1">
                        <span class="inline-block w-2 h-2 mt-0.5 bg-memphis-teal border border-black shrink-0" />
                        <span>强：≥8位且含3种以上字符</span>
                      </li>
                    </ul>
                    <p class="font-mono text-xs text-black/60 mt-2 border-t-2 border-black pt-2">
                      字符类型：小写、大写、数字、特殊符号
                    </p>
                    <!-- 小三角 -->
                    <div class="absolute -bottom-2 right-3 w-0 h-0 border-l-[6px] border-l-transparent border-r-[6px] border-r-transparent border-t-[8px] border-t-black" />
                    <div class="absolute -bottom-1 right-[13px] w-0 h-0 border-l-[5px] border-l-transparent border-r-[5px] border-r-transparent border-t-[6px] border-t-white" />
                  </div>
                </div>
              </div>
            </div>
            <!-- 密码强度条（仅注册时显示） -->
            <div v-if="!isLogin && form.password" class="flex items-center gap-2 mt-2">
              <div class="flex gap-1 flex-1">
                <div
                  v-for="i in 3"
                  :key="i"
                  class="h-2 flex-1 border-2 border-black transition-colors duration-200"
                  :class="i <= passwordStrength
                    ? (passwordStrength === 1 ? 'bg-memphis-coral'
                      : passwordStrength === 2 ? 'bg-memphis-yellow'
                      : 'bg-memphis-teal')
                    : 'bg-black/10'"
                />
              </div>
              <span
                class="font-black text-xs tracking-wider"
                :class="passwordStrength === 1 ? 'text-memphis-coral'
                  : passwordStrength === 2 ? 'text-memphis-yellow'
                  : 'text-memphis-teal'"
              >{{ strengthLabels[passwordStrength] }}</span>
            </div>
            <p v-if="errors.password" class="text-memphis-coral font-mono text-xs mt-1">{{ errors.password }}</p>
          </div>

          <!-- 注册：确认密码 -->
          <div v-if="!isLogin">
            <label class="block font-black text-sm mb-2">确认密码</label>
            <input
              v-model="form.confirmPassword"
              :type="showPassword ? 'text' : 'password'"
              placeholder="请再次输入密码"
              class="w-full memphis-input px-4 py-3 text-sm md:text-base"
              :class="{ 'border-memphis-coral': errors.confirmPassword }"
            />
            <p v-if="errors.confirmPassword" class="text-memphis-coral font-mono text-xs mt-1">{{ errors.confirmPassword }}</p>
          </div>

          <!-- 全局错误消息 -->
          <div v-if="errorMessage" class="bg-memphis-coral/10 border-4 border-memphis-coral p-3 font-mono text-sm text-memphis-coral">
            {{ errorMessage }}
          </div>

          <!-- 成功消息 -->
          <div v-if="successMessage" class="bg-memphis-teal/10 border-4 border-memphis-teal p-3 font-mono text-sm">
            {{ successMessage }}
          </div>

          <!-- 提交按钮 -->
          <button
            type="submit"
            :disabled="isSubmitting"
            :class="[
              'w-full font-black py-3 md:py-4 text-sm md:text-base memphis-btn-primary',
              isLogin
                ? 'bg-memphis-coral text-white'
                : registerMode === 'email'
                  ? 'bg-memphis-coral text-white'
                  : 'bg-memphis-blue text-white'
            ]"
          >
            {{ isSubmitting ? '处理中...' : (isLogin ? '登 录' : '注 册') }}
          </button>
        </form>

        <!-- 切换登录/注册 -->
        <div class="mt-6 text-center font-mono text-sm">
          <span v-if="isLogin">
            还没有账号？
            <button @click="switchToRegister" class="font-black text-memphis-coral hover:underline">立即注册</button>
          </span>
          <span v-else>
            已有账号？
            <button @click="switchToLogin" class="font-black text-memphis-coral hover:underline">去登录</button>
          </span>
        </div>
      </div>

      <!-- 底部装饰 -->
      <div class="mt-6 text-center font-mono text-xs text-gray-600">
        <router-link to="/" class="hover:text-memphis-coral transition-colors">← 返回首页</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isLogin = ref(true)
const registerMode = ref<'email' | 'username'>('email')
const showPassword = ref(false)
const showStrengthTip = ref(false)
const isSubmitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const form = reactive({
  account: '',
  email: '',
  username: '',
  password: '',
  confirmPassword: '',
})

// 密码强度：0=空 1=弱 2=中 3=强
const passwordStrength = computed(() => {
  const pw = form.password
  if (!pw) return 0
  let score = 0
  if (/[a-z]/.test(pw)) score++
  if (/[A-Z]/.test(pw)) score++
  if (/\d/.test(pw)) score++
  if (/[^a-zA-Z0-9]/.test(pw)) score++
  if (pw.length < 6) return 1
  if (pw.length < 8 && score < 3) return 2
  return 3
})

const strengthLabels = ['', '弱', '中', '强'] as const

const errors = reactive({
  account: '',
  email: '',
  username: '',
  password: '',
  confirmPassword: '',
})

function clearErrors() {
  errors.account = ''
  errors.email = ''
  errors.username = ''
  errors.password = ''
  errors.confirmPassword = ''
  errorMessage.value = ''
  successMessage.value = ''
}

function clearForm() {
  form.account = ''
  form.email = ''
  form.username = ''
  form.password = ''
  form.confirmPassword = ''
  clearErrors()
}

function switchToRegister() {
  isLogin.value = false
  clearForm()
}

function switchToLogin() {
  isLogin.value = true
  clearForm()
}

function validateLogin(): boolean {
  let valid = true
  clearErrors()

  if (!form.account.trim()) {
    errors.account = '请输入邮箱或用户名'
    valid = false
  }
  if (!form.password) {
    errors.password = '请输入密码'
    valid = false
  }
  return valid
}

function validateRegister(): boolean {
  let valid = true
  clearErrors()

  if (registerMode.value === 'email') {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!form.email.trim()) {
      errors.email = '请输入邮箱地址'
      valid = false
    } else if (!emailRegex.test(form.email)) {
      errors.email = '请输入有效的邮箱地址'
      valid = false
    }
  } else {
    if (!form.username.trim()) {
      errors.username = '请输入用户名'
      valid = false
    } else if (form.username.trim().length < 3) {
      errors.username = '用户名至少需要3个字符'
      valid = false
    } else if (!/^[a-zA-Z0-9_\u4e00-\u9fa5]+$/.test(form.username.trim())) {
      errors.username = '用户名只能包含字母、数字、下划线和中文'
      valid = false
    }
  }

  if (!form.password) {
    errors.password = '请输入密码'
    valid = false
  } else if (form.password.length < 6) {
    errors.password = '密码至少需要6位'
    valid = false
  }

  if (!form.confirmPassword) {
    errors.confirmPassword = '请确认密码'
    valid = false
  } else if (form.password !== form.confirmPassword) {
    errors.confirmPassword = '两次输入的密码不一致'
    valid = false
  }

  return valid
}

async function handleSubmit() {
  if (isLogin.value ? !validateLogin() : !validateRegister()) return

  isSubmitting.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    if (isLogin.value) {
      const result = await authStore.login(form.account.trim(), form.password)
      if (result.success) {
        successMessage.value = result.message
        setTimeout(() => router.push('/dashboard'), 800)
      } else {
        errorMessage.value = result.message
      }
    } else {
      const result =
        registerMode.value === 'email'
          ? await authStore.registerByEmail(form.email.trim(), form.password)
          : await authStore.registerByUsername(form.username.trim(), form.password)

      if (result.success) {
        successMessage.value = result.message
        setTimeout(() => router.push('/dashboard'), 800)
      } else {
        errorMessage.value = result.message
      }
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>
