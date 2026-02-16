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
        <div class="cart-icon">
          <i class="fas fa-shopping-cart"></i>
          <span class="cart-count">0</span>
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