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
          <div v-for="product in products" :key="product.id" class="product-card" @click="goToProduct(product.id)">
            <img :src="product.image" :alt="product.name" class="product-image">
            <h3 class="product-name">{{ product.name }}</h3>
            <p class="product-price">${{ product.price.toFixed(2) }}</p>
            <button class="add-to-cart" @click.stop="addToCart(product)">Add to Cart</button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { products } from '../data/products' // import the shared array

export default {
  name: 'Products',
  data() {
    return {
      products: products // use it directly
    }
  },
  methods: {
    goToProduct(id) {
      this.$router.push(`/product/${id}`)
    },
    addToCart(product) {
      console.log('Added to cart:', product)
    }
  }
}
</script>