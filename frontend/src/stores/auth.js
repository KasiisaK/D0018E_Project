// stores/auth.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token'))
  const user = ref(null)

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.isAdmin || false)

  async function fetchUser() {
    if (!token.value) return
    try {
      const response = await api.get('/api/user')
      const userData = response.data.user
      // /api/user returns snake_case: user_id, username, is_admin
      user.value = {
        id: userData.user_id,
        username: userData.username,
        isAdmin: userData.is_admin   // convert to camelCase
      }
    } catch (error) {
      console.error('Failed to fetch user', error)
      logout()
    }
  }

  function setAuth(data) {
    user.value = {
      id: data.user.id,
      username: data.user.username,
      isAdmin: data.user.isAdmin   // keep this
    }
    token.value = data.token
    localStorage.setItem('token', data.token)
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }

  return { user, token, isAuthenticated, isAdmin, fetchUser, setAuth, logout }
})