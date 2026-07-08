<template>
  <AdminLayout v-if="route.meta.layout === 'admin'">
    <router-view />
  </AdminLayout>
  <DefaultLayout v-else-if="route.meta.layout !== 'none'">
    <router-view />
  </DefaultLayout>
  <router-view v-else />
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import DefaultLayout from '@/components/DefaultLayout.vue'
import AdminLayout from '@/components/AdminLayout.vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const authStore = useAuthStore()
authStore.init()
</script>
