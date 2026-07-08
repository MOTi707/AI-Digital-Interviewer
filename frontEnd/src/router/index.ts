import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
    meta: { layout: 'default' },
  },
  {
    path: '/auth',
    name: 'Auth',
    component: () => import('@/views/AuthView.vue'),
    meta: { layout: 'none' },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { layout: 'none', requiresAuth: true },
  },
  {
    path: '/resume',
    name: 'Resume',
    component: () => import('@/views/ResumeView.vue'),
    meta: { layout: 'none', requiresAuth: true },
  },
  {
    path: '/resume/optimize',
    name: 'ResumeOptimize',
    component: () => import('@/views/ResumeOptimizeView.vue'),
    meta: { layout: 'none', requiresAuth: true },
  },
  {
    path: '/oj/problem/:id',
    name: 'OJProblem',
    component: () => import('@/views/OJProblemView.vue'),
    meta: { layout: 'none', requiresAuth: true },
  },
  {
    path: '/career/test/:type',
    name: 'CareerTest',
    component: () => import('@/views/CareerTestView.vue'),
    meta: { layout: 'none', requiresAuth: true },
  },
  {
    path: '/career/result/:id',
    name: 'CareerResult',
    component: () => import('@/views/CareerResultView.vue'),
    meta: { layout: 'none', requiresAuth: true },
  },
  {
    path: '/career/history',
    name: 'CareerHistory',
    component: () => import('@/views/CareerHistoryView.vue'),
    meta: { layout: 'none', requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { layout: 'none', requiresAuth: true },
  },
  {
    path: '/settings',
    name: 'AccountSettings',
    component: () => import('@/views/AccountSettingsView.vue'),
    meta: { layout: 'none', requiresAuth: true },
  },
  {
    path: '/interview/session/:id',
    name: 'InterviewSession',
    component: () => import('@/views/InterviewSessionView.vue'),
    meta: { layout: 'none', requiresAuth: true },
  },
  {
    path: '/interview/report/:id',
    name: 'InterviewReport',
    component: () => import('@/views/InterviewReportView.vue'),
    meta: { layout: 'none', requiresAuth: true },
  },
  {
    path: '/interview/history',
    name: 'InterviewHistory',
    component: () => import('@/views/InterviewHistoryView.vue'),
    meta: { layout: 'none', requiresAuth: true },
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('@/views/admin/AdminLoginView.vue'),
    meta: { layout: 'none' },
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: () => import('@/views/admin/AdminDashboard.vue'),
    meta: { layout: 'admin', requiresAdmin: true },
  },
  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: () => import('@/views/admin/AdminUsers.vue'),
    meta: { layout: 'admin', requiresAdmin: true },
  },
  {
    path: '/admin/problems',
    name: 'AdminProblems',
    component: () => import('@/views/admin/AdminProblems.vue'),
    meta: { layout: 'admin', requiresAdmin: true },
  },
  {
    path: '/admin/posts',
    name: 'AdminPosts',
    component: () => import('@/views/admin/AdminPosts.vue'),
    meta: { layout: 'admin', requiresAdmin: true },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, _from, savedPosition) {
    if (to.hash) {
      return {
        el: to.hash,
        behavior: 'smooth',
      }
    }
    return savedPosition || { top: 0 }
  },
})

// 路由守卫：需要登录的页面跳转至 /auth，已登录用户访问 /auth 跳转至 /dashboard
// 管理端守卫：需要管理员登录，未登录跳转 /admin/login
router.beforeEach((to, _from) => {
  const authStore = useAuthStore()

  // 管理员路由守卫
  if (to.meta.requiresAdmin) {
    const isAdmin = localStorage.getItem('admin_auth') === 'true'
    if (!isAdmin) {
      return { name: 'AdminLogin' }
    }
  }

  // 已登录管理员访问登录页，直接跳转管理后台
  if (to.name === 'AdminLogin') {
    const isAdmin = localStorage.getItem('admin_auth') === 'true'
    if (isAdmin) {
      return { name: 'AdminDashboard' }
    }
  }

  // 普通用户路由守卫
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return { name: 'Auth' }
  }
  if (to.name === 'Auth' && authStore.isAuthenticated) {
    return { name: 'Dashboard' }
  }
})

export default router
