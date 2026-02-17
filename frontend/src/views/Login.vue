<template>
  <div class="auth-page">
    <div class="container">
      <div class="auth-form">
        <h2>Log In</h2>
        <form @submit.prevent="handleLogin">
          <div class="form-group">
            <label for="email">Email</label>
            <input type="email" id="email" v-model="email" required>
          </div>
          <div class="form-group">
            <label for="password">Password</label>
            <input type="password" id="password" v-model="password" required>
          </div>
          <button type="submit" :disabled="loading">Log In</button>
          <p v-if="error" class="error">{{ error }}</p>
        </form>
        <p>Don't have an account? <router-link to="/signup">Sign up</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

export default {
  setup() {
    const email = ref('')
    const password = ref('')
    const loading = ref(false)
    const error = ref('')
    const authStore = useAuthStore()
    const router = useRouter()

    const handleLogin = async () => {
      loading.value = true
      error.value = ''
      try {
        const response = await fetch('/api/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: email.value, password: password.value })
        })
        const data = await response.json()
        if (response.ok) {
          authStore.setAuth(data)
          router.push('/') // or to previous page
        } else {
          error.value = data.message || 'Login failed'
        }
      } catch (err) {
        error.value = 'Network error'
      } finally {
        loading.value = false
      }
    }

    return { email, password, loading, error, handleLogin }
  }
}
</script>

<style scoped>
.auth-page {
  padding: 60px 20px;
  min-height: 60vh;
}
.auth-form {
  max-width: 400px;
  margin: 0 auto;
  background: #fff;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}
.auth-form h2 {
  margin-bottom: 20px;
  color: #2c3e50;
}
.form-group {
  margin-bottom: 15px;
}
.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
}
.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #bdc3c7;
  border-radius: 8px;
  font-size: 1rem;
}
button {
  width: 100%;
  padding: 12px;
  background-color: #8b5a2b;
  color: #fff;
  border: none;
  border-radius: 30px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}
button:hover:not(:disabled) {
  background-color: #6b441e;
}
button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.error {
  color: #e74c3c;
  margin-top: 10px;
  text-align: center;
}
</style>