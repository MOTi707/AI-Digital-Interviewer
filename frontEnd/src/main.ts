import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import './style.css'
import App from './App.vue'
import { useAuthStore } from './stores/auth'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// 恢复登录态（验证本地 token）
const authStore = useAuthStore()
authStore.init().then(() => {
  app.mount('#app')
})
