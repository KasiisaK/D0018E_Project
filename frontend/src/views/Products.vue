<template>
  <div>
    <!-- Page Header -->
    <div class="container" style="padding: 40px 20px 20px;">
      <h1 class="section-title">All Mugs</h1>
      <p style="text-align: center; color: #7f8c8d; margin-bottom: 30px;">
        Browse our collection of handcrafted mugs
      </p>
    </div>
    <!-- Products Grid -->
    <section class="products">
      <div class="container">
        <div class="product-grid">
          <div
            v-for="product in products"
            :key="product.product_id"
            class="product-card"
            @click="goToProduct(product.product_id)"
          >
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

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '../stores/cart'
import api from '../api/index'

const router = useRouter()
const cartStore = useCartStore()
const products = ref([])

onMounted(async () => {
  try {
    const response = await api.get('/products')
    products.value = response.data
  } catch (err) {
    console.error('Failed to load products:', err)
  }
})

function addToCart(product) {
  cartStore.addToCart(product.product_id, 1)
}

function goToProduct(id) {
  console.log(`Navigating to product, id: ${id}`)
  router.push(`/product/${id}`)
}
</script>