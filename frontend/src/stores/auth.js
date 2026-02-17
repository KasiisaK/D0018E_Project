import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)

  const isAuthenticated = computed(() => !!token.value)

  // Set auth data after login/signup
  function setAuth(data) {
    user.value = data.user
    token.value = data.token
    localStorage.setItem('token', data.token)
  }

  // Clear auth on logout
  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  // Example: fetch current user (call after app load if token exists)
  async function fetchUser() {
    if (!token.value) return
    try {
      const response = await fetch('/api/user', {
        headers: { Authorization: `Bearer ${token.value}` }
      })
      if (response.ok) {
        const data = await response.json()
        user.value = data.user
      } else {
        // Token invalid
        logout()
      }
    } catch (error) {
      console.error('Failed to fetch user', error)
      logout()
    }
  }

  return { user, token, isAuthenticated, setAuth, logout, fetchUser }
})