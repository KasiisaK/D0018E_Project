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
        <h2 class="section-title">Our Best Sellers</h2>
        <div class="product-grid">
          <div v-for="product in products" :key="product.id" class="product-card" @click="goToProduct(product.id)">
            <img :src="product.image" :alt="product.name" class="product-image">
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
import { useCartStore } from '../stores/cart'   // <-- import the cart store
import mug1 from '../assets/images/mug1.png'

export default {
  data() {
    return {
      products: [
        { id: 1, name: 'mugmug', price: 9.99, image: mug1 },
        { id: 2, name: 'mug', price: 9.99, image: mug1 },
        { id: 3, name: 'mug', price: 9.99, image: mug1 },
        { id: 4, name: 'mug', price: 9.99, image: mug1 },
      ]
    }
  },
  methods: {
    goToProduct(id) {
      this.$router.push(`/product/${id}`)
    },
    addToCart(product) {
      const cartStore = useCartStore()          // <-- get the store instance
      cartStore.addToCart(product, 1)            // add one item
      alert(`Added ${product.name} to cart!`)
    }
  }
}
</script>