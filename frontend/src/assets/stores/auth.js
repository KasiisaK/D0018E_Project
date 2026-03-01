import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api/index'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)

  const isAuthenticated = computed(() => !!token.value)

  // Set auth data after login/signup
  function setAuth(data) {
    user.value = data.username
    token.value = data.token
    console.log('Auth set:', { user: user.value, token: token.value }) // Debug log
    localStorage.setItem('token', data.token)
  }

  // clear auth on logout
  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  // Fetch user data if token exists (e.g. on page refresh)
  async function fetchUser() {
    if (!token.value) return
    try {
      const response = await api.get('/api/user')
      user.value = response.data.user
    } catch {
      logout()
    }
  }

  return { user, token, isAuthenticated, setAuth, logout, fetchUser }
})