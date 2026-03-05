<template>
  <div class="product-detail-page">
    <!-- Breadcrumb -->
    <div class="container">
      <div class="breadcrumb">
        <router-link to="/">Home</router-link> &gt;
        <router-link to="/products">Shop</router-link> &gt;
        <span v-if="product">{{ product.name }}</span>
        <span v-else>Loading...</span>
      </div>
    </div>

    <!-- Loading / error states -->
    <div v-if="loading" class="container text-center" style="padding: 100px 20px;">
      <p>Loading product details...</p>
    </div>
    <div v-else-if="error" class="container text-center" style="padding: 100px 20px; color: #e74c3c;">
      <h2>Error</h2>
      <p>{{ error }}</p>
      <router-link to="/products">Back to Shop</router-link>
    </div>

    <!-- Product Detail (only when product is loaded) -->
    <section v-else-if="product" class="product-detail">
      <div class="container">
        <div class="product-detail-grid">
          <!-- Left: Images -->
          <div class="product-images">
            <div class="main-image">
              <img :src="product.image_url" :alt="product.name">
            </div>
          </div>

          <!-- Right: Product info -->
          <div class="product-info">
            <h1 class="product-title">{{ product.name }}</h1>
            <p class="product-price-detail">
              € {{ Number(product.price)?.toFixed(2) || '0.00' }}
            </p>

            <!-- Star rating (average) -->
            <div class="product-rating">
              <i v-for="star in fullStars" :key="'full'+star" class="fas fa-star"></i>
              <i v-if="hasHalfStar" class="fas fa-star-half-alt"></i>
              <i v-for="star in emptyStars" :key="'empty'+star" class="far fa-star"></i>
              <span>{{ Number(product.average_rating || 0)?.toFixed(1) }}</span>
              <span>({{ product.review_count || 0 }} reviews)</span>
            </div>

            <p class="product-description">
              {{ product.description || 'No description available.' }}
            </p>

            <div class="product-actions">
              <div class="quantity-selector">
                <label for="quantity">Quantity:</label>
                <input
                  type="number"
                  id="quantity"
                  v-model.number="quantity"
                  min="1"
                  :max="product.stock_quantity"
                />
              </div>
              <button class="btn add-to-cart-detail" @click="addToCart">
                Add to Cart
              </button>
            </div>
          </div>
        </div>

        <!-- Reviews component -->
        <ProductComments
          :productId="product.product_id"
          @review-submitted="refreshProduct"
          @review-updated="refreshProduct"
          @review-deleted="refreshProduct"
        />
      </div>
    </section>

    <!-- Fallback if product is null but no error (shouldn't happen) -->
    <div v-else class="container text-center" style="padding: 100px 20px;">
      <p>Product not found.</p>
      <router-link to="/products">Back to Shop</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useCartStore } from '../stores/cart'
import api from '../api/index'
import ProductComments from '../components/ProductComments.vue'

const route = useRoute()
const cartStore = useCartStore()

const product = ref(null)
const loading = ref(true)
const error = ref(null)
const quantity = ref(1)

onMounted(async () => {
  const id = route.params.id

  if (!id) {
    error.value = 'No product ID in URL'
    loading.value = false
    return
  }

  try {
    console.log(`Fetching product with ID: ${id}`)
    const response = await api.get(`/product/${id}`)

    console.log('API response:', response.data)
    if (!response.data) {
      error.value = 'Product not found'
      product.value = null
    } else {
      product.value = response.data
    }
  } catch (err) {
    console.error('Failed to load product:', err)
    error.value = err.response?.data?.message || 'Could not load product details'
  } finally {
    loading.value = false
  }
})

function addToCart() {
  if (!product.value) return
  cartStore.addToCart(product.value.product_id, quantity.value)
}

const refreshProduct = async () => {
  const id = route.params.id
  try {
    const response = await api.get(`/product/${id}`)
    product.value = response.data
  } catch (err) {
    console.error('Failed to refresh product:', err)
  }
}

const fullStars   = computed(() => Math.floor(Number(product.value?.average_rating || 0)))
const hasHalfStar = computed(() => Number(product.value?.average_rating || 0) % 1 >= 0.5)
const emptyStars  = computed(() => 5 - Math.ceil(Number(product.value?.average_rating || 0)))
</script>