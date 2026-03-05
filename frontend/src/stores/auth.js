// stores/auth.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  // Initialize token from localStorage
  const token = ref(localStorage.getItem('token'))
  const user = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  // Fetch current user data using the token
  async function fetchUser() {
    if (!token.value) return
    try {
      const response = await api.get('/api/user')
      user.value = response.data.user
    } catch (error) {
      console.error('Failed to fetch user', error)
      logout() // token invalid – logout
    }
  }

  // Set auth data after login/register
  function setAuth(data) {
    token.value = data.token
    user.value = data.user
    localStorage.setItem('token', data.token)
  }

  // Logout – clear state and localStorage
  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }

  return { user, token, isAuthenticated, fetchUser, setAuth, logout }
})