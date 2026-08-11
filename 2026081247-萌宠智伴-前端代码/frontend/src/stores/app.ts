import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface UserInfo {
  id: number
  username: string
  role: 'student' | 'teacher' | 'admin'
  avatar?: string
  name?: string
}

export const useAppStore = defineStore('app', () => {
  const user = ref<UserInfo | null>(null)
  const token = ref<string | null>(null)
  const collapsed = ref(false)

  const isLoggedIn = computed(() => !!token.value && !!user.value)

  function setUser(u: UserInfo | null) { user.value = u }
  function setToken(t: string | null) { token.value = t }
  function setCollapsed(v: boolean) { collapsed.value = v }
  function logout() { user.value = null; token.value = null; localStorage.removeItem('pet-education-storage') }

  function persist() {
    localStorage.setItem('pet-education-storage', JSON.stringify({ user: user.value, token: token.value }))
  }

  function load() {
    const raw = localStorage.getItem('pet-education-storage')
    if (raw) {
      try {
        const d = JSON.parse(raw)
        user.value = d.user || null
        token.value = d.token || null
      } catch { /* ignore */ }
    }
  }

  return { user, token, collapsed, isLoggedIn, setUser, setToken, setCollapsed, logout, persist, load }
})
