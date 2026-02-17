<template>
  <div id="app" class="app-wrapper">
    <nav class="navbar">
      <div class="container">
        <router-link to="/" class="logo">bigMug</router-link>
        <div class="nav-links">
          <router-link to="/">Home</router-link>
          <router-link to="/products">Shop</router-link>
          <router-link to="/about">About</router-link>
          <a href="#">Contact</a>
        </div>
        <div class="nav-right">
          <template v-if="authStore.isAuthenticated">
            <span class="user-greeting">Hi, {{ authStore.user?.name }}</span>
            <button @click="logout" class="logout-btn">Logout</button>
          </template>
          <template v-else>
            <router-link to="/login" class="nav-link">Login</router-link>
          </template>
          <div class="cart-icon">
            <i class="fas fa-shopping-cart"></i>
            <span class="cart-count">{{ cartCount }}</span>
          </div>
        </div>
      </div>
    </nav>

    <main class="main-content">
      <router-view />
    </main>

    <footer class="footer">
      <div class="container">
        <p>&copy; 2026 bigMug | All rights reserved.</p>
        <p><a href="#">Privacy Policy</a> | <a href="#">Terms of Service</a></p>
      </div>
    </footer>
  </div>
</template>

<script>
import { useAuthStore } from './stores/auth'
import { computed } from 'vue'
import { useRouter } from 'vue-router'

export default {
  setup() {
    const authStore = useAuthStore()
    const router = useRouter()

    // cart count
    const cartCount = computed(() => 2) // placeholder

    const logout = () => {
      authStore.logout()
      router.push('/')
    }

    return { authStore, cartCount, logout }
  }
}
</script>