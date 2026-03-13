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
            <span class="user-greeting">Hi, {{ authStore.user?.username }}</span>
            <!-- Admin button – only visible if user is admin -->
            <button v-if="authStore.isAdmin" @click="showAdminModal = true" class="admin-btn">
              Admin Panel
            </button>
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
    <!--DEBUGLINE-->
    <div style="background:yellow;">Admin status: {{ authStore.isAdmin }}</div>
    
    <!-- Admin Panel Modal -->
    <AdminPanel :show="showAdminModal" @close="showAdminModal = false" />

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
import { ref, onMounted, watch } from 'vue'
import { useCartStore } from './stores/cart'
import { useAuthStore } from './stores/auth'
import AdminPanel from './components/AdminPanel.vue'  // <-- import the new component

const cartStore = useCartStore()
const authStore = useAuthStore()
const showAdminModal = ref(false)  // controls modal visibility

onMounted(async () => {
  await authStore.fetchUser()
  if (authStore.isAuthenticated) {
    await cartStore.fetchCart()
  }
})

watch(
  () => authStore.isAuthenticated,
  async (isAuth) => {
    if (isAuth) {
      await cartStore.fetchCart()
    } else {
      cartStore.items = []
    }
  },
  { immediate: true }
)

const logout = () => {
  authStore.logout()
}
</script>

<style scoped>
/* Add a style for the admin button */
.admin-btn {
  background: #333;
  color: white;
  border: none;
  padding: 0.4rem 0.8rem;
  margin-right: 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}
.admin-btn:hover {
  background: #555;
}
/* existing styles remain */
</style>