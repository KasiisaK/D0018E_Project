<template>
  <div class="product-detail-page">
    <!-- Breadcrumb -->
    <div class="container">
      <div class="breadcrumb">
        <router-link to="/">Home</router-link> &gt; 
        <router-link to="/products">Shop</router-link> &gt; 
        <span>{{ product.name }}</span>
      </div>
    </div>

    <!-- Product Detail Section -->
    <section class="product-detail">
      <div class="container">
        <div class="product-detail-grid">
          <!-- left section: Images -->
          <div class="product-images">
            <div class="main-image">
              <!-- Show the active thumbnail or fallback to product.image -->
              <img :src="product.thumbnails[activeThumb] || product.image" :alt="product.name">
            </div>
            <div class="thumbnail-images">
              <img v-for="(thumb, index) in product.thumbnails" :key="index" 
                   :src="thumb" alt="Thumbnail" class="thumbnail" 
                   :class="{ active: index === activeThumb }" 
                   @click="activeThumb = index">
            </div>
          </div>

          <!-- right section: Product info -->
          <div class="product-info">
            <h1 class="product-title">{{ product.name }}</h1>
            <p class="product-price-detail">${{ product.price.toFixed(2) }}</p>
            <div class="product-rating">
              <i v-for="star in fullStars" :key="'full'+star" class="fas fa-star"></i>
              <i v-if="hasHalfStar" class="fas fa-star-half-alt"></i>
              <i v-for="star in emptyStars" :key="'empty'+star" class="far fa-star"></i>
              <span>({{ product.reviews }} reviews)</span>
            </div>
            <p class="product-description">{{ product.description }}</p>

            <div class="product-details">
              <h3>Details</h3>
              <ul>
                <li v-for="(value, key) in product.specs" :key="key">
                  <strong>{{ key }}:</strong> {{ value }}
                </li>
              </ul>
            </div>

            <div class="product-actions">
              <div class="quantity-selector">
                <label for="quantity">Quantity:</label>
                <input type="number" id="quantity" v-model.number="quantity" min="1" max="10">
              </div>
              <button class="btn add-to-cart-detail" @click="addToCart">Add to Cart</button>
            </div>

            <div class="product-meta">
              <p><strong>Category:</strong> {{ product.category }}</p>
              <p><strong>Tags:</strong> {{ product.tags.join(', ') }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { products } from '../data/products'          // shared product data
import { useCartStore } from '../stores/cart'       // <-- import the cart store

export default {
  data() {
    return {
      activeThumb: 0,
      quantity: 1,
      products: products
    }
  },
  computed: {
    product() {
      const id = parseInt(this.$route.params.id)
      return this.products.find(p => p.id === id) || this.products[0]
    },
    fullStars() {
      return Math.floor(this.product.rating)
    },
    hasHalfStar() {
      return this.product.rating % 1 !== 0
    },
    emptyStars() {
      return 5 - Math.ceil(this.product.rating)
    }
  },
  methods: {
    addToCart() {
      const cartStore = useCartStore()               // get the store instance

      // Prepare the product object that the cart expects
      const productToAdd = {
        id: this.product.id,
        name: this.product.name,
        price: this.product.price,
        // Use the main image, or fallback to first thumbnail if needed
        image: this.product.image || (this.product.thumbnails && this.product.thumbnails[0]) || 'https://via.placeholder.com/80'
      }

      cartStore.addToCart(productToAdd, this.quantity)

      // Optional: give the user some feedback
      alert(`Added ${this.quantity} × ${this.product.name} to cart!`)
    }
  }
}
</script>