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
            :key="product.id" 
            class="product-card" 
            @click="goToProduct(product.id)"
          >
            <img :src="product.image" :alt="product.name" class="product-image">
            <h3 class="product-name">{{ product.name }}</h3>
            <p class="product-price">${{ product.price.toFixed(2) }}</p>
            <!-- Add .stop to prevent the card's click event from firing -->
            <button class="add-to-cart" @click.stop="addToCart(product)">Add to Cart</button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { useCartStore } from '../stores/cart'
import { products } from '../data/products'      // <-- import the shared product data
import { useRouter } from 'vue-router'           // <-- for navigation

export default {
  setup() {
    const cartStore = useCartStore()
    const router = useRouter()

    const addToCart = (product) => {
      cartStore.addToCart(product, 1)
      alert(`Added ${product.name} to cart!`)
    }

    const goToProduct = (id) => {
      router.push(`/product/${id}`)
    }

    return { 
      products,      // <-- make products available to the template
      addToCart, 
      goToProduct 
    }
  }
}
</script>