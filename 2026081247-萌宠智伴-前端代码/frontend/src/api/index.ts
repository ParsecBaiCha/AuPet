import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const raw = localStorage.getItem('pet-education-storage')
  if (raw) {
    try {
      const state = JSON.parse(raw)
      if (state.token) config.headers.Authorization = `Bearer ${state.token}`
    } catch { /* ignore */ }
  }
  return config
})

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const msg = error.response?.data?.message || '请求失败'
    if (error.response?.status === 401) {
      localStorage.removeItem('pet-education-storage')
      window.location.href = '/login'
    }
    // 支持 _silent 选项：页面初始加载等场景静默处理错误
    if (!error.config?._silent) {
      ElMessage.error(msg)
    }
    return Promise.reject(error)
  }
)

export default api
