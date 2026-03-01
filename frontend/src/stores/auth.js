import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)

  const isAuthenticated = computed(() => !!token.value)

  // Set auth data after login/signup
  function setAuth(data) {
    user.value = {
      id: data.user.id,
      name: data.user.username,
    }

    token.value = data.token
    localStorage.setItem('token', data.token)
  }

  // Clear auth on logout
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
      user.value = response.data.name
    } catch (error) {
      console.error('Failed to fetch user', error)
      logout() // Clear auth if token is invalid/expired
    }
  }

  return { user, token, isAuthenticated, setAuth, logout, fetchUser }
})