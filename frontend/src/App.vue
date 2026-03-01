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
          <router-link to="/cart" class="cart-icon">
            <i class="fas fa-shopping-cart"></i>
            <span class="cart-count">{{ cartStore.totalTypes }}</span>
          </router-link>
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

<script setup>
import { useCartStore } from './stores/cart'
import { useAuthStore } from './stores/auth'
import { onMounted, watch } from 'vue' // watch to update cart on login/logout

const cartStore = useCartStore()
const authStore = useAuthStore()

onMounted(async () => {
  // Initial load: restore user + cart if already logged in
  await authStore.fetchUser()
  if (authStore.isAuthenticated) {
    await cartStore.fetchCart()
  }
})

// Watch auth stare and update cart icon accordingly
watch(
  () => authStore.isAuthenticated,
  async (isAuth) => {
    if (isAuth) {
      await cartStore.fetchCart()
    } else {
      cartStore.items = []  // clear locally
    }
  },
  { immediate: true }  // run once on mount too
)

const logout = () => {
  authStore.logout()
}
</script>