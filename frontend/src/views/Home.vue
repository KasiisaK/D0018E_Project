<template>
  <div>
    <!-- Hero Section -->
    <section class="hero">
      <div class="container">
        <h1>Start Your Day with the Perfect Mug</h1>
        <p>Handcrafted, unique designs that make your coffee taste better.</p>
        <router-link to="/products" class="btn">Shop Now</router-link>
      </div>
    </section>

    <!-- Products Section -->
    <section class="products">
      <div class="container">
        <h2 class="section-title">Our Best Sellers Test</h2>
        <div class="product-grid">
          <div v-for="product in products" :key="product.product_id" class="product-card" @click="goToProduct(product.product_id)">
            <img :src="product.image_url" :alt="product.name" class="product-image">
            <h3 class="product-name">{{ product.name }}</h3>
            <p class="product-price">€ {{ product.price }}</p>
            <button class="add-to-cart" @click.stop="addToCart(product)">Add to Cart</button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { useCartStore } from '../stores/cart'
import { ref, onMounted } from 'vue'
import api from '../api/index'
import { useRouter } from 'vue-router'

export default {
  setup() {
    const cartStore = useCartStore()
    const products = ref([])
    const router = useRouter()

    onMounted(async () => {
      const response = await api.get('/api/products/bestSellers')
      products.value = response.data
    })

    function addToCart(product) {
      cartStore.addToCart(product.product_id, 1)
    }

    function goToProduct(id) {
      router.push(`/product/${id}`)
    }

    return { products, addToCart, goToProduct}
  }
}
</script>