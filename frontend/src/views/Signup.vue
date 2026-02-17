<template>
  <div class="auth-page">
    <div class="container">
      <div class="auth-form">
        <h2>Sign Up</h2>
        <form @submit.prevent="handleSignup">
          <div class="form-group">
            <label for="name">Name</label>
            <input type="text" id="name" v-model="name" required>
          </div>
          <div class="form-group">
            <label for="email">Email</label>
            <input type="email" id="email" v-model="email" required>
          </div>
          <div class="form-group">
            <label for="password">Password</label>
            <input type="password" id="password" v-model="password" required>
          </div>
          <div class="form-group">
            <label for="confirmPassword">Confirm Password</label>
            <input type="password" id="confirmPassword" v-model="confirmPassword" required>
          </div>
          <button type="submit" :disabled="loading">Sign Up</button>
          <p v-if="error" class="error">{{ error }}</p>
        </form>
        <p>Already have an account? <router-link to="/login">Log in</router-link></p>
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
    const name = ref('')
    const email = ref('')
    const password = ref('')
    const confirmPassword = ref('')
    const loading = ref(false)
    const error = ref('')
    const authStore = useAuthStore()
    const router = useRouter()

    const handleSignup = async () => {
      if (password.value !== confirmPassword.value) {
        error.value = 'Passwords do not match'
        return
      }
      loading.value = true
      error.value = ''
      try {
        const response = await fetch('/api/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            name: name.value, 
            email: email.value, 
            password: password.value 
          })
        })
        const data = await response.json()
        if (response.ok) {
          authStore.setAuth(data) // auto-login
          router.push('/')
        } else {
          error.value = data.message || 'Signup failed'
        }
      } catch (err) {
        error.value = 'Network error'
      } finally {
        loading.value = false
      }
    }

    return { name, email, password, confirmPassword, loading, error }
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
  background-color: #c71818;
  color: #fff;
  border: none;
  border-radius: 30px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}
button:hover:not(:disabled) {
  background-color: #2c3e50;
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